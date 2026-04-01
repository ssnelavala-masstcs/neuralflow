import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.run import NodeRun, Run
from neuralflow.models.workflow import Workflow
from neuralflow.schemas.run import NodeRunOut, RunCreate, RunOut

router = APIRouter(prefix="/api/runs")

# Map of run_id → asyncio.Queue for SSE event delivery
_run_queues: dict[str, asyncio.Queue] = {}


def get_run_queue(run_id: str) -> asyncio.Queue | None:
    return _run_queues.get(run_id)


def create_run_queue(run_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _run_queues[run_id] = q
    return q


def cleanup_run_queue(run_id: str) -> None:
    _run_queues.pop(run_id, None)


@router.post("", response_model=RunOut, status_code=201)
async def start_run(body: RunCreate, db: AsyncSession = Depends(get_db)):
    wf = await db.get(Workflow, body.workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")

    run = Run(
        workflow_id=body.workflow_id,
        workflow_snapshot=wf.canvas_data,
        status="queued",
        trigger_type=body.trigger_type,
        input_data=json.dumps(body.input_data) if body.input_data else None,
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    # Create SSE queue and kick off execution in background
    create_run_queue(run.id)
    asyncio.create_task(_execute_run(run.id, body.workflow_id, body.input_data))

    return run


@router.get("/{run_id}", response_model=RunOut)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run


@router.get("/{run_id}/nodes", response_model=list[NodeRunOut])
async def list_node_runs(run_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NodeRun).where(NodeRun.run_id == run_id))
    return result.scalars().all()


@router.get("/{run_id}/stream")
async def stream_run(run_id: str):
    """SSE endpoint — streams execution events as they happen."""
    queue = get_run_queue(run_id)
    if queue is None:
        # Run already finished; return empty stream
        async def empty():
            yield "data: {\"type\":\"done\"}\n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") in ("done", "error"):
                    break
        finally:
            cleanup_run_queue(run_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/{run_id}/cancel", status_code=200)
async def cancel_run(run_id: str, db: AsyncSession = Depends(get_db)):
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    if run.status not in ("queued", "running"):
        raise HTTPException(400, f"Cannot cancel a run in state: {run.status}")
    run.status = "cancelled"
    await db.commit()
    q = get_run_queue(run_id)
    if q:
        await q.put({"type": "cancelled", "run_id": run_id})
    return {"ok": True}


@router.get("", response_model=list[RunOut])
async def list_runs(workflow_id: str | None = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    stmt = select(Run).order_by(Run.started_at.desc()).limit(limit)
    if workflow_id:
        stmt = stmt.where(Run.workflow_id == workflow_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def _execute_run(run_id: str, workflow_id: str, input_data: dict | None) -> None:
    """Background task that drives execution and pushes SSE events."""
    from neuralflow.database import AsyncSessionLocal
    from neuralflow.execution.orchestrator import Orchestrator

    async with AsyncSessionLocal() as db:
        queue = get_run_queue(run_id)
        try:
            orchestrator = Orchestrator(db=db, run_id=run_id, event_queue=queue)
            await orchestrator.execute(workflow_id=workflow_id, input_data=input_data)
        except Exception as exc:
            if queue:
                await queue.put({"type": "error", "run_id": run_id, "message": str(exc)})
