from datetime import datetime
from typing import Any

from pydantic import BaseModel


class RunCreate(BaseModel):
    workflow_id: str
    input_data: dict[str, Any] | None = None
    trigger_type: str = "manual"


class RunOut(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger_type: str
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int

    model_config = {"from_attributes": True}


class NodeRunOut(BaseModel):
    id: str
    run_id: str
    node_id: str
    node_type: str
    node_name: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    error_message: str | None
    cost_usd: float
    input_tokens: int
    output_tokens: int

    model_config = {"from_attributes": True}


class LlmCallOut(BaseModel):
    id: str
    node_run_id: str
    provider: str
    model: str
    call_index: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int | None
    finish_reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Debug / Replay schemas ────────────────────────────────────────────────────

class ToolCallDetail(BaseModel):
    id: str
    name: str
    source: str
    input: dict[str, Any]
    output: Any
    error: str | None
    latency_ms: int | None


class LlmCallDetail(BaseModel):
    id: str
    model: str
    call_index: int
    messages: list[dict[str, Any]]
    response_content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int | None
    finish_reason: str | None
    tool_calls: list[ToolCallDetail]


class RunStepOut(BaseModel):
    id: str
    node_id: str
    node_name: str
    node_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    cost_usd: float
    input_tokens: int
    output_tokens: int
    output_data: dict[str, Any] | None
    error_message: str | None
    llm_call_count: int
    tool_call_count: int
    llm_calls: list[LlmCallDetail]
