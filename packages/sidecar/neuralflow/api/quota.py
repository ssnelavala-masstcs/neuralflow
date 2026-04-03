"""Quota management API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from neuralflow.services.quota_manager import get_quota, set_quota, get_usage, QuotaConfig

router = APIRouter(prefix="/api/quota")


@router.get("")
async def get_quota_status() -> dict[str, Any]:
    """Get current quota configuration and usage."""
    return {
        "quota": get_quota().to_dict(),
        "usage": get_usage().to_dict(),
    }


@router.patch("")
async def update_quota(body: dict[str, Any]) -> dict[str, Any]:
    """Update quota configuration."""
    current = get_quota()
    config = QuotaConfig(
        monthly_budget_usd=body.get("monthly_budget_usd", current.monthly_budget_usd),
        daily_budget_usd=body.get("daily_budget_usd", current.daily_budget_usd),
        per_run_budget_usd=body.get("per_run_budget_usd", current.per_run_budget_usd),
        alert_threshold_pct=body.get("alert_threshold_pct", current.alert_threshold_pct),
        hard_stop_at_budget=body.get("hard_stop_at_budget", current.hard_stop_at_budget),
        provider_rate_limits=body.get("provider_rate_limits", current.provider_rate_limits),
    )
    set_quota(config)
    return {"quota": config.to_dict()}


@router.post("/reset")
async def reset_usage() -> dict[str, Any]:
    """Reset current run usage tracker."""
    get_usage().reset_run()
    return {"usage": get_usage().to_dict()}
