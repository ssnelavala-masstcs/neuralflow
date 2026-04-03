"""Swarm executor API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from neuralflow.execution.swarm_executor import SwarmExecutor, SwarmWorker, SwarmStrategy

router = APIRouter(prefix="/api/swarm")

_executor = SwarmExecutor()


@router.post("/execute")
async def execute_swarm(body: dict[str, Any]) -> dict[str, Any]:
    """Execute a swarm of agents in parallel."""
    workers_data = body.get("workers", [])
    inputs = body.get("inputs", [])
    strategy = body.get("strategy", "fan_out")
    aggregator = body.get("aggregator", "concat")

    workers = [
        SwarmWorker(
            id=w["id"],
            model=w["model"],
            system_prompt=w["system_prompt"],
            max_tokens=w.get("max_tokens", 4096),
        )
        for w in workers_data
    ]

    try:
        strat = SwarmStrategy(strategy)
    except ValueError:
        return {"error": f"Invalid strategy: {strategy}. Must be one of: fan_out, replicate, specialize"}

    # Note: This requires an agent_runner instance which is created during workflow execution.
    # For direct API calls, we return the configuration for the orchestrator to execute.
    return {
        "swarm_config": {
            "workers": [w.to_dict() if hasattr(w, "to_dict") else str(w) for w in workers],
            "strategy": strat.value,
            "aggregator": aggregator,
            "input_count": len(inputs),
        },
        "message": "Swarm execution requires workflow context. Use the workflow run endpoint.",
    }


@router.get("/{swarm_id}")
async def get_swarm_results(swarm_id: str) -> dict[str, Any]:
    """Get results from a completed swarm execution."""
    results = _executor.get_swarm_results(swarm_id)
    if results is None:
        return {"error": "Swarm not found"}
    return {"results": [r.to_dict() for r in results]}
