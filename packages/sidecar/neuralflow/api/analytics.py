"""Cost and usage analytics endpoints."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.run import LlmCall, Run

router = APIRouter(prefix="/api/analytics")


@router.get("/costs")
async def get_cost_analytics(
    workflow_id: str | None = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Returns cost aggregations:
    - per_day: [{date, cost_usd, input_tokens, output_tokens, run_count}]
    - per_model: [{model, cost_usd, input_tokens, output_tokens, call_count}]
    - per_workflow: [{workflow_id, cost_usd, run_count}]
    - totals: {cost_usd, input_tokens, output_tokens, run_count}
    - budget_alert_threshold: float | None  (placeholder, settable via PATCH)
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Base run filter
    run_filter = [Run.started_at >= since]
    if workflow_id:
        run_filter.append(Run.workflow_id == workflow_id)

    # ── Per-day aggregation from Run table ─────────────────────────────────
    day_stmt = (
        select(
            func.date(Run.started_at).label("day"),
            func.sum(Run.total_cost_usd).label("cost_usd"),
            func.sum(Run.total_input_tokens).label("input_tokens"),
            func.sum(Run.total_output_tokens).label("output_tokens"),
            func.count(Run.id).label("run_count"),
        )
        .where(*run_filter)
        .group_by(func.date(Run.started_at))
        .order_by(func.date(Run.started_at))
    )
    day_rows = (await db.execute(day_stmt)).all()

    # Fill gaps — return 0 entries for days with no runs
    all_days: list[dict] = []
    for i in range(days):
        d = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).date()
        row = next((r for r in day_rows if str(r.day) == str(d)), None)
        all_days.append({
            "date": str(d),
            "cost_usd": round(float(row.cost_usd or 0), 6) if row else 0.0,
            "input_tokens": int(row.input_tokens or 0) if row else 0,
            "output_tokens": int(row.output_tokens or 0) if row else 0,
            "run_count": int(row.run_count or 0) if row else 0,
        })

    # ── Per-model aggregation from LlmCall table ───────────────────────────
    model_stmt = (
        select(
            LlmCall.model,
            func.sum(LlmCall.cost_usd).label("cost_usd"),
            func.sum(LlmCall.input_tokens).label("input_tokens"),
            func.sum(LlmCall.output_tokens).label("output_tokens"),
            func.count(LlmCall.id).label("call_count"),
        )
        .where(LlmCall.run_id.in_(
            select(Run.id).where(*run_filter)
        ))
        .group_by(LlmCall.model)
        .order_by(func.sum(LlmCall.cost_usd).desc())
    )
    model_rows = (await db.execute(model_stmt)).all()
    per_model = [
        {
            "model": r.model,
            "cost_usd": round(float(r.cost_usd or 0), 6),
            "input_tokens": int(r.input_tokens or 0),
            "output_tokens": int(r.output_tokens or 0),
            "call_count": int(r.call_count or 0),
        }
        for r in model_rows
    ]

    # ── Per-workflow aggregation ────────────────────────────────────────────
    wf_stmt = (
        select(
            Run.workflow_id,
            func.sum(Run.total_cost_usd).label("cost_usd"),
            func.count(Run.id).label("run_count"),
        )
        .where(*run_filter)
        .group_by(Run.workflow_id)
        .order_by(func.sum(Run.total_cost_usd).desc())
        .limit(20)
    )
    wf_rows = (await db.execute(wf_stmt)).all()
    per_workflow = [
        {
            "workflow_id": r.workflow_id,
            "cost_usd": round(float(r.cost_usd or 0), 6),
            "run_count": int(r.run_count or 0),
        }
        for r in wf_rows
    ]

    # ── Totals ──────────────────────────────────────────────────────────────
    totals_stmt = select(
        func.sum(Run.total_cost_usd),
        func.sum(Run.total_input_tokens),
        func.sum(Run.total_output_tokens),
        func.count(Run.id),
    ).where(*run_filter)
    totals_row = (await db.execute(totals_stmt)).one()

    return {
        "per_day": all_days,
        "per_model": per_model,
        "per_workflow": per_workflow,
        "totals": {
            "cost_usd": round(float(totals_row[0] or 0), 6),
            "input_tokens": int(totals_row[1] or 0),
            "output_tokens": int(totals_row[2] or 0),
            "run_count": int(totals_row[3] or 0),
        },
        "period_days": days,
    }
