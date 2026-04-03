"""AI Builder API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from neuralflow.services.ai_builder import generate_workflow

router = APIRouter(prefix="/api/ai-builder")


@router.post("/generate")
async def generate_workflow_from_description(body: dict[str, Any]) -> dict[str, Any]:
    """Generate a workflow from a natural language description."""
    description = body.get("description", "")
    workflow = generate_workflow(description)
    return workflow
