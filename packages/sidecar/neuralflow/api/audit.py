"""Audit log API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from neuralflow.middleware.audit_log import audit_log

router = APIRouter(prefix="/api/audit")


@router.get("/logs")
async def get_audit_logs(
    method: str | None = Query(None),
    path_prefix: str | None = Query(None),
    status_min: int | None = Query(None),
    status_max: int | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
) -> dict[str, Any]:
    """Retrieve audit log entries."""
    logs = audit_log.query(
        method=method,
        path_prefix=path_prefix,
        status_min=status_min,
        status_max=status_max,
        limit=limit,
    )
    return {"logs": logs, "total": audit_log.total_entries}


@router.delete("/logs")
async def clear_audit_logs() -> dict[str, Any]:
    """Clear all audit logs."""
    audit_log.clear()
    return {"message": "Audit logs cleared"}
