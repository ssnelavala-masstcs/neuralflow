"""Tests for cost estimation service."""
import pytest
from neuralflow.services.cost_estimator import estimate_workflow, CostEstimate


def test_empty_workflow():
    result = estimate_workflow([], [])
    assert result.estimated_input_tokens == 0
    assert result.estimated_output_tokens == 0
    assert result.estimated_cost_usd == 0.0


def test_single_agent_gpt4o():
    nodes = [
        {
            "id": "agent-1",
            "type": "agent",
            "data": {
                "model": "gpt-4o",
                "system_prompt": "You are a helpful assistant.",
                "max_tokens": 4096,
            },
        }
    ]
    result = estimate_workflow(nodes, [])
    assert result.estimated_input_tokens > 0
    assert result.estimated_output_tokens > 0
    assert result.estimated_cost_usd > 0
    assert len(result.per_node) == 1
    assert result.per_node[0]["model"] == "gpt-4o"


def test_multiple_agents():
    nodes = [
        {
            "id": "agent-1",
            "type": "agent",
            "data": {"model": "gpt-4o", "system_prompt": "Research agent.", "max_tokens": 2048},
        },
        {
            "id": "agent-2",
            "type": "agent",
            "data": {"model": "gpt-4o-mini", "system_prompt": "Summary agent.", "max_tokens": 1024},
        },
    ]
    result = estimate_workflow(nodes, [])
    assert len(result.per_node) == 2
    assert result.estimated_cost_usd > 0
    assert result.low_estimate_usd < result.estimated_cost_usd
    assert result.high_estimate_usd > result.estimated_cost_usd


def test_unknown_model_uses_default_pricing():
    nodes = [
        {
            "id": "agent-1",
            "type": "agent",
            "data": {"model": "some-unknown-model", "system_prompt": "Test.", "max_tokens": 1000},
        }
    ]
    result = estimate_workflow(nodes, [])
    assert result.estimated_cost_usd > 0
