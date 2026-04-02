"""Scheduled trigger CRUD API."""
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.schedule import ScheduledTrigger

router = APIRouter(prefix="/api/schedules")


class ScheduleCreate(BaseModel):
    workflow_id: str
    trigger_type: str  # cron | webhook | file_watch
    cron_expression: str | None = None
    webhook_path: str | None = None
    watch_path: str | None = None
    input_data: dict[str, Any] | None = None


class ScheduleOut(BaseModel):
    id: str
    workflow_id: str
    trigger_type: str
    cron_expression: str | None
    webhook_path: str | None
    watch_path: str | None
    input_data: dict[str, Any] | None
    is_active: bool
    trigger_count: int

    model_config = {"from_attributes": True}


@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(body: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    if body.trigger_type == "cron" and not body.cron_expression:
        raise HTTPException(400, "cron_expression required for cron trigger")
    if body.trigger_type == "webhook" and not body.webhook_path:
        raise HTTPException(400, "webhook_path required for webhook trigger")
    if body.trigger_type == "file_watch" and not body.watch_path:
        raise HTTPException(400, "watch_path required for file_watch trigger")

    t = ScheduledTrigger(
        workflow_id=body.workflow_id,
        trigger_type=body.trigger_type,
        cron_expression=body.cron_expression,
        webhook_path=body.webhook_path,
        watch_path=body.watch_path,
        input_data=json.dumps(body.input_data) if body.input_data else None,
        is_active=True,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)

    # Register with APScheduler if cron
    if t.trigger_type == "cron" and t.cron_expression:
        from neuralflow.scheduling.scheduler import schedule_cron_trigger
        schedule_cron_trigger(t.id, t.workflow_id, t.cron_expression, body.input_data)

    return t


@router.get("", response_model=list[ScheduleOut])
async def list_schedules(workflow_id: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(ScheduledTrigger)
    if workflow_id:
        stmt = stmt.where(ScheduledTrigger.workflow_id == workflow_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("/{schedule_id}", status_code=200)
async def delete_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    t = await db.get(ScheduledTrigger, schedule_id)
    if not t:
        raise HTTPException(404, "Schedule not found")

    from neuralflow.scheduling.scheduler import unschedule_trigger
    unschedule_trigger(schedule_id)

    await db.delete(t)
    await db.commit()
    return {"ok": True}


@router.patch("/{schedule_id}/toggle", response_model=ScheduleOut)
async def toggle_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    t = await db.get(ScheduledTrigger, schedule_id)
    if not t:
        raise HTTPException(404, "Schedule not found")

    t.is_active = not t.is_active
    await db.commit()

    from neuralflow.scheduling.scheduler import schedule_cron_trigger, unschedule_trigger
    if t.is_active and t.trigger_type == "cron" and t.cron_expression:
        input_d = json.loads(t.input_data) if t.input_data else None
        schedule_cron_trigger(t.id, t.workflow_id, t.cron_expression, input_d)
    else:
        unschedule_trigger(t.id)

    return t


@router.post("/webhook/{webhook_path}")
async def receive_webhook(webhook_path: str, db: AsyncSession = Depends(get_db)):
    """Incoming webhook fires matching scheduled triggers."""
    import asyncio
    from neuralflow.api.runs import create_run_queue, _execute_run
    from neuralflow.models.run import Run
    from neuralflow.models.workflow import Workflow

    result = await db.execute(
        select(ScheduledTrigger).where(
            ScheduledTrigger.trigger_type == "webhook",
            ScheduledTrigger.webhook_path == webhook_path,
            ScheduledTrigger.is_active == True,  # noqa: E712
        )
    )
    triggers = result.scalars().all()
    if not triggers:
        raise HTTPException(404, f"No active webhook trigger at path: {webhook_path}")

    fired: list[str] = []
    for t in triggers:
        wf = await db.get(Workflow, t.workflow_id)
        if not wf:
            continue
        input_d = json.loads(t.input_data) if t.input_data else None
        run = Run(
            workflow_id=t.workflow_id,
            workflow_snapshot=wf.canvas_data,
            status="queued",
            trigger_type="webhook",
            input_data=t.input_data,
        )
        db.add(run)
        await db.flush()
        fired.append(run.id)
        create_run_queue(run.id)
        asyncio.create_task(_execute_run(run.id, t.workflow_id, input_d))

    await db.commit()
    return {"fired_runs": fired}
