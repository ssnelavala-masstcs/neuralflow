"""Sub-agent API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from neuralflow.services.subagent import SubAgentConfig, subagent_manager

router = APIRouter(prefix="/api/subagent")


@router.post("/spawn")
async def spawn_subagents(body: dict[str, Any]) -> dict[str, Any]:
    """Spawn sub-agents for parallel execution.

    Note: Actual execution requires an AgentRunner instance from the
    workflow execution context. This endpoint validates the configuration
    and returns the execution plan.
    """
    configs_data = body.get("sub_agents", [])
    input_data = body.get("input_data", {})

    configs = [
        SubAgentConfig(
            name=c["name"],
            role=c.get("role", ""),
            system_prompt=c.get("system_prompt", ""),
            model=c.get("model", "gpt-4o"),
            max_iterations=c.get("max_iterations", 10),
            max_tokens=c.get("max_tokens", 4096),
        )
        for c in configs_data
    ]

    return {
        "execution_plan": {
            "sub_agents": [
                {
                    "name": c.name,
                    "role": c.role,
                    "model": c.model,
                    "max_iterations": c.max_iterations,
                    "max_tokens": c.max_tokens,
                }
                for c in configs
            ],
            "input_data": input_data,
            "parallel": True,
            "expected_workers": len(configs),
        },
        "message": "Sub-agent execution requires workflow context. Use the workflow run endpoint.",
    }


@router.post("/config")
async def validate_subagent_config(body: dict[str, Any]) -> dict[str, Any]:
    """Validate a sub-agent configuration."""
    errors = []
    if not body.get("name"):
        errors.append("Name is required")
    if not body.get("system_prompt"):
        errors.append("System prompt is required")
    if not body.get("model"):
        errors.append("Model is required")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }
