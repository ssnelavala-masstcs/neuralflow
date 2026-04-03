"""Cost estimation for workflow runs."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("neuralflow.cost_estimator")

# Pricing per 1M tokens (USD) — approximate as of 2025
_MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "o3-mini": {"input": 1.10, "output": 4.40},
    "o1": {"input": 15.00, "output": 60.00},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-haiku-3-5-20241022": {"input": 0.80, "output": 4.00},
    "llama-3.3-70b": {"input": 0.70, "output": 0.90},
    "mixtral-8x7b": {"input": 0.24, "output": 0.24},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "deepseek-chat": {"input": 0.14, "output": 0.28},
}

_DEFAULT_PRICING = {"input": 1.00, "output": 5.00}


@dataclass
class CostEstimate:
    """Estimated cost for a workflow run."""

    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    low_estimate_usd: float = 0.0
    high_estimate_usd: float = 0.0
    per_node: list[dict[str, Any]] = field(default_factory=list)
    model_pricing_used: list[str] = field(default_factory=list)


def estimate_workflow(nodes: list[dict], edges: list[dict]) -> CostEstimate:
    """Estimate cost based on workflow structure and node configurations."""
    estimate = CostEstimate()
    agent_nodes = [n for n in nodes if n.get("type") == "agent"]

    for node in agent_nodes:
        data = node.get("data", {})
        model = data.get("model", "")
        system_prompt = data.get("system_prompt", "")
        max_tokens = data.get("max_tokens", 4096)

        # Estimate input tokens from system prompt + expected input
        input_tokens = len(system_prompt.encode()) + 500  # base input overhead
        # Estimate output tokens as 50% of max_tokens (typical utilization)
        output_tokens = int(max_tokens * 0.5)

        # Get pricing
        pricing = _MODEL_PRICING.get(model, _DEFAULT_PRICING)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        estimate.estimated_input_tokens += input_tokens
        estimate.estimated_output_tokens += output_tokens
        estimate.estimated_cost_usd += total_cost
        estimate.low_estimate_usd += total_cost * 0.5
        estimate.high_estimate_usd += total_cost * 2.0
        estimate.model_pricing_used.append(model)

        estimate.per_node.append({
            "node_id": node.get("id"),
            "node_name": data.get("label", node.get("id")),
            "model": model,
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_usd": round(total_cost, 6),
        })

    estimate.estimated_cost_usd = round(estimate.estimated_cost_usd, 6)
    estimate.low_estimate_usd = round(estimate.low_estimate_usd, 6)
    estimate.high_estimate_usd = round(estimate.high_estimate_usd, 6)

    return estimate
