"""APScheduler singleton: manages cron-based workflow trigger jobs."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

log = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler(timezone="UTC")
    return _scheduler


def start_scheduler() -> None:
    sched = get_scheduler()
    if not sched.running:
        sched.start()
        log.info("APScheduler started")


def stop_scheduler() -> None:
    sched = get_scheduler()
    if sched.running:
        sched.shutdown(wait=False)
        log.info("APScheduler stopped")


def schedule_cron_trigger(trigger_id: str, workflow_id: str, cron_expr: str, input_data: dict | None) -> None:
    """Add or replace a cron job for a ScheduledTrigger."""
    sched = get_scheduler()
    job_id = f"trigger_{trigger_id}"

    # Remove existing job if present
    if sched.get_job(job_id):
        sched.remove_job(job_id)

    # Parse cron_expr: "minute hour day month day_of_week" (5-field standard)
    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: '{cron_expr}' (expected 5 fields)")

    minute, hour, day, month, day_of_week = parts
    trigger = CronTrigger(
        minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week
    )

    sched.add_job(
        _fire_trigger,
        trigger=trigger,
        id=job_id,
        kwargs={"trigger_id": trigger_id, "workflow_id": workflow_id, "input_data": input_data},
        replace_existing=True,
        misfire_grace_time=60,
    )
    log.info("Scheduled cron trigger %s for workflow %s: %s", trigger_id, workflow_id, cron_expr)


def unschedule_trigger(trigger_id: str) -> None:
    sched = get_scheduler()
    job_id = f"trigger_{trigger_id}"
    if sched.get_job(job_id):
        sched.remove_job(job_id)
        log.info("Removed cron job for trigger %s", trigger_id)


async def _fire_trigger(trigger_id: str, workflow_id: str, input_data: dict | None) -> None:
    """Called by APScheduler when a cron fires. Creates a Run and executes it."""
    from neuralflow.database import AsyncSessionLocal
    from neuralflow.models.run import Run
    from neuralflow.api.runs import create_run_queue, _execute_run
    from neuralflow.models.schedule import ScheduledTrigger

    log.info("Firing trigger %s for workflow %s", trigger_id, workflow_id)

    async with AsyncSessionLocal() as db:
        trigger = await db.get(ScheduledTrigger, trigger_id)
        if not trigger or not trigger.is_active:
            return

        from neuralflow.models.workflow import Workflow
        wf = await db.get(Workflow, workflow_id)
        if not wf:
            log.warning("Workflow %s not found for trigger %s", workflow_id, trigger_id)
            return

        run = Run(
            workflow_id=workflow_id,
            workflow_snapshot=wf.canvas_data,
            status="queued",
            trigger_type="cron",
            input_data=json.dumps(input_data) if input_data else None,
        )
        db.add(run)

        trigger.last_triggered_at = datetime.now(timezone.utc)
        trigger.trigger_count = (trigger.trigger_count or 0) + 1
        await db.commit()
        await db.refresh(run)

    create_run_queue(run.id)
    asyncio.create_task(_execute_run(run.id, workflow_id, input_data))


async def reload_all_triggers() -> None:
    """On startup: load all active cron triggers from DB and re-register them."""
    from neuralflow.database import AsyncSessionLocal
    from neuralflow.models.schedule import ScheduledTrigger
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ScheduledTrigger).where(
                ScheduledTrigger.is_active == True,  # noqa: E712
                ScheduledTrigger.trigger_type == "cron",
                ScheduledTrigger.cron_expression.isnot(None),
            )
        )
        triggers = result.scalars().all()

    for t in triggers:
        try:
            import json as _json
            input_d = _json.loads(t.input_data) if t.input_data else None
            schedule_cron_trigger(t.id, t.workflow_id, t.cron_expression, input_d)
        except Exception as exc:
            log.warning("Could not reload trigger %s: %s", t.id, exc)

    log.info("Reloaded %d cron triggers from DB", len(triggers))
