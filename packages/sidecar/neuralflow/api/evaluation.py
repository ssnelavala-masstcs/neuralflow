import asyncio
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.evaluation import Evaluation
from neuralflow.models.run import Run
from neuralflow.models.workflow import Workflow
from neuralflow.schemas.evaluation import EvaluationCreate, EvaluationOut

router = APIRouter(prefix="/api/evaluations")


@router.post("", response_model=EvaluationOut, status_code=201)
async def create_evaluation(body: EvaluationCreate, db: AsyncSession = Depends(get_db)):
    # Validate both workflows exist
    wf_a = await db.get(Workflow, body.workflow_a_id)
    wf_b = await db.get(Workflow, body.workflow_b_id)
    if not wf_a:
        raise HTTPException(404, f"Workflow A (id={body.workflow_a_id}) not found")
    if not wf_b:
        raise HTTPException(404, f"Workflow B (id={body.workflow_b_id}) not found")

    evaluation = Evaluation(
        id=str(uuid.uuid4()),
        workflow_a_id=body.workflow_a_id,
        workflow_b_id=body.workflow_b_id,
        test_input=json.dumps(body.test_input),
        metric=body.metric,
        status="pending",
    )
    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    # Kick off evaluation in background
    asyncio.create_task(_run_evaluation(evaluation.id))

    return EvaluationOut.from_orm_model(evaluation)


@router.get("", response_model=list[EvaluationOut])
async def list_evaluations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Evaluation).order_by(Evaluation.created_at.desc()))
    evaluations = result.scalars().all()
    return [EvaluationOut.from_orm_model(e) for e in evaluations]


@router.get("/{eval_id}", response_model=EvaluationOut)
async def get_evaluation(eval_id: str, db: AsyncSession = Depends(get_db)):
    evaluation = await db.get(Evaluation, eval_id)
    if not evaluation:
        raise HTTPException(404, "Evaluation not found")
    return EvaluationOut.from_orm_model(evaluation)


@router.delete("/{eval_id}", status_code=204)
async def delete_evaluation(eval_id: str, db: AsyncSession = Depends(get_db)):
    evaluation = await db.get(Evaluation, eval_id)
    if not evaluation:
        raise HTTPException(404, "Evaluation not found")
    await db.delete(evaluation)
    await db.commit()


async def _run_workflow_and_collect(workflow_id: str, input_data: dict | None) -> dict:
    """Execute a workflow run synchronously and return collected metrics."""
    from neuralflow.database import AsyncSessionLocal
    from neuralflow.execution.orchestrator import Orchestrator
    from neuralflow.api.runs import create_run_queue, cleanup_run_queue, get_run_queue

    async with AsyncSessionLocal() as db:
        # Create a run record
        wf = await db.get(Workflow, workflow_id)
        if not wf:
            raise ValueError(f"Workflow {workflow_id} not found")

        run = Run(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            workflow_snapshot=wf.canvas_data,
            status="queued",
            trigger_type="evaluation",
            input_data=json.dumps(input_data) if input_data else None,
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        # Create SSE queue for event delivery
        create_run_queue(run.id)

        try:
            orchestrator = Orchestrator(db=db, run_id=run.id, event_queue=get_run_queue(run.id))
            await orchestrator.execute(workflow_id=workflow_id, input_data=input_data)
        except Exception as exc:
            run.status = "error"
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            await db.commit()
            raise
        finally:
            cleanup_run_queue(run.id)

        # Refresh to get final values
        await db.refresh(run)

        # Parse output
        output = None
        if run.output_data:
            try:
                output = json.loads(run.output_data)
            except (json.JSONDecodeError, TypeError):
                output = run.output_data

        return {
            "run_id": run.id,
            "cost_usd": run.total_cost_usd,
            "total_tokens": run.total_input_tokens + run.total_output_tokens,
            "duration_ms": run.duration_ms,
            "output": output,
            "status": run.status,
        }


async def _run_evaluation(eval_id: str) -> None:
    """Background task that runs both workflows and stores results."""
    from neuralflow.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        evaluation = await db.get(Evaluation, eval_id)
        if not evaluation:
            return

        evaluation.status = "running"
        await db.commit()

        try:
            test_input = json.loads(evaluation.test_input) if isinstance(evaluation.test_input, str) else evaluation.test_input

            # Run both workflows concurrently
            result_a_task = asyncio.create_task(_run_workflow_and_collect(evaluation.workflow_a_id, test_input))
            result_b_task = asyncio.create_task(_run_workflow_and_collect(evaluation.workflow_b_id, test_input))

            result_a, result_b = await asyncio.gather(result_a_task, result_b_task, return_exceptions=True)

            # Handle exceptions
            if isinstance(result_a, Exception):
                evaluation.status = "error"
                evaluation.error_message = f"Workflow A failed: {result_a}"
                await db.commit()
                return
            if isinstance(result_b, Exception):
                evaluation.status = "error"
                evaluation.error_message = f"Workflow B failed: {result_b}"
                await db.commit()
                return

            evaluation.result_a = json.dumps(result_a)
            evaluation.result_b = json.dumps(result_b)
            evaluation.status = "complete"
            evaluation.completed_at = datetime.now(timezone.utc)
            await db.commit()

        except Exception as exc:
            evaluation.status = "error"
            evaluation.error_message = str(exc)
            await db.commit()
