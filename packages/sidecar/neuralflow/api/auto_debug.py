"""Auto-debug API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from neuralflow.services.auto_debug import diagnose_failure

router = APIRouter(prefix="/api/debug")


@router.post("/diagnose")
async def diagnose_run_failure(body: dict[str, Any]) -> dict[str, Any]:
    """Diagnose a workflow failure and suggest fixes."""
    report = diagnose_failure(
        error_message=body.get("error_message", ""),
        node_type=body.get("node_type"),
        node_config=body.get("node_config"),
        llm_calls=body.get("llm_calls"),
        tool_calls=body.get("tool_calls"),
    )
    return report.to_dict()
