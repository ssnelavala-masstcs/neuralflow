import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.run import NodeRun, Run
from neuralflow.models.workflow import Workflow
from neuralflow.models.run import LlmCall, ToolCallRecord
from neuralflow.schemas.run import LlmCallDetail, NodeRunOut, RunCreate, RunOut, RunStepOut, ToolCallDetail

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
async def list_runs(workflow_id: str | None = None, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    stmt = select(Run).order_by(Run.started_at.desc()).offset(offset).limit(limit)
    if workflow_id:
        stmt = stmt.where(Run.workflow_id == workflow_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/count")
async def count_runs(workflow_id: str | None = None, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func
    stmt = select(func.count()).select_from(Run)
    if workflow_id:
        stmt = stmt.where(Run.workflow_id == workflow_id)
    result = await db.execute(stmt)
    return {"count": result.scalar_one()}


@router.get("/{run_id}/steps", response_model=list[RunStepOut])
async def get_run_steps(run_id: str, db: AsyncSession = Depends(get_db)):
    """Return all node steps for a run, each with its full LLM call and tool call trace."""
    from neuralflow.execution.replay_engine import load_run_replay
    replay = await load_run_replay(run_id, db)
    return [
        RunStepOut(
            id=s.id,
            node_id=s.node_id,
            node_name=s.node_name,
            node_type=s.node_type,
            status=s.status,
            started_at=s.started_at,
            completed_at=s.completed_at,
            duration_ms=s.duration_ms,
            cost_usd=s.cost_usd,
            input_tokens=s.input_tokens,
            output_tokens=s.output_tokens,
            output_data=s.output_data,
            error_message=s.error_message,
            llm_call_count=s.llm_call_count,
            tool_call_count=s.tool_call_count,
            llm_calls=[
                LlmCallDetail(
                    id=lc.id,
                    model=lc.model,
                    call_index=lc.call_index,
                    messages=lc.messages,
                    response_content=lc.response_content,
                    input_tokens=lc.input_tokens,
                    output_tokens=lc.output_tokens,
                    cost_usd=lc.cost_usd,
                    latency_ms=lc.latency_ms,
                    finish_reason=lc.finish_reason,
                    tool_calls=[
                        ToolCallDetail(
                            id=tc.id, name=tc.name, source=tc.source,
                            input=tc.input, output=tc.output,
                            error=tc.error, latency_ms=tc.latency_ms,
                        )
                        for tc in lc.tool_calls
                    ],
                )
                for lc in s.llm_calls
            ],
        )
        for s in replay.steps
    ]


@router.post("/{run_id}/resume", status_code=200)
async def resume_run(run_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    """Supply human input for a run paused at a HumanNode."""
    from neuralflow.execution.hitl import resolve_resume_gate
    run = await db.get(Run, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    if run.status != "awaiting_input":
        raise HTTPException(400, f"Run is not awaiting input (status: {run.status})")
    if not resolve_resume_gate(run_id, body):
        raise HTTPException(409, "No active human gate for this run")
    return {"ok": True}


@router.post("/{run_id}/rerun-from/{node_run_id}", response_model=dict, status_code=201)
async def rerun_from_step(run_id: str, node_run_id: str, db: AsyncSession = Depends(get_db)):
    """Fork a new run, replaying all steps up to (not including) the given node_run_id."""
    original = await db.get(Run, run_id)
    if not original:
        raise HTTPException(404, "Run not found")

    # Verify node_run belongs to this run
    pivot = await db.get(NodeRun, node_run_id)
    if not pivot or pivot.run_id != run_id:
        raise HTTPException(404, "NodeRun not found in this run")

    # Create new run forked from original's snapshot
    new_run = Run(
        workflow_id=original.workflow_id,
        workflow_snapshot=original.workflow_snapshot,
        status="queued",
        trigger_type="replay",
        input_data=original.input_data,
        metadata_=json.dumps({"forked_from": run_id, "from_node_run_id": node_run_id}),
    )
    db.add(new_run)
    await db.commit()
    await db.refresh(new_run)

    create_run_queue(new_run.id)
    asyncio.create_task(_execute_run(new_run.id, original.workflow_id, json.loads(original.input_data) if original.input_data else None))

    return {"new_run_id": new_run.id}


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
