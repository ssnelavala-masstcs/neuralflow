"""Replay engine: loads run trace from SQLite and reconstructs step-by-step state."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.models.run import LlmCall, NodeRun, Run, ToolCallRecord


@dataclass
class ToolCallStep:
    id: str
    name: str
    source: str
    input: dict[str, Any]
    output: Any
    error: str | None
    latency_ms: int | None


@dataclass
class LlmCallStep:
    id: str
    model: str
    call_index: int
    messages: list[dict]
    response_content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: int | None
    finish_reason: str | None
    tool_calls: list[ToolCallStep] = field(default_factory=list)


@dataclass
class NodeStep:
    id: str
    node_id: str
    node_name: str
    node_type: str
    status: str
    started_at: Any
    completed_at: Any
    duration_ms: int | None
    cost_usd: float
    input_tokens: int
    output_tokens: int
    output_data: dict | None
    error_message: str | None
    llm_calls: list[LlmCallStep] = field(default_factory=list)

    @property
    def llm_call_count(self) -> int:
        return len(self.llm_calls)

    @property
    def tool_call_count(self) -> int:
        return sum(len(c.tool_calls) for c in self.llm_calls)


@dataclass
class RunReplay:
    run_id: str
    workflow_id: str
    status: str
    trigger_type: str
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    started_at: Any
    completed_at: Any
    duration_ms: int | None
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    steps: list[NodeStep] = field(default_factory=list)


async def load_run_replay(run_id: str, db: AsyncSession) -> RunReplay:
    """Load a complete run trace from the database."""
    run = await db.get(Run, run_id)
    if not run:
        raise ValueError(f"Run {run_id} not found")

    # Load node runs ordered by start time
    nr_result = await db.execute(
        select(NodeRun)
        .where(NodeRun.run_id == run_id)
        .order_by(NodeRun.started_at)
    )
    node_runs = nr_result.scalars().all()

    steps: list[NodeStep] = []
    for nr in node_runs:
        # Load LLM calls for this node run
        lc_result = await db.execute(
            select(LlmCall)
            .where(LlmCall.node_run_id == nr.id)
            .order_by(LlmCall.call_index)
        )
        llm_calls_raw = lc_result.scalars().all()

        llm_call_steps: list[LlmCallStep] = []
        for lc in llm_calls_raw:
            # Load tool calls for this LLM call
            tc_result = await db.execute(
                select(ToolCallRecord)
                .where(ToolCallRecord.llm_call_id == lc.id)
            )
            tool_calls_raw = tc_result.scalars().all()

            tool_steps = [
                ToolCallStep(
                    id=tc.id,
                    name=tc.tool_name,
                    source=tc.tool_source,
                    input=_parse_json(tc.input_data, {}),
                    output=_parse_json(tc.output_data, None),
                    error=tc.error,
                    latency_ms=tc.latency_ms,
                )
                for tc in tool_calls_raw
            ]

            response_obj = _parse_json(lc.response, {})
            response_content = ""
            try:
                response_content = response_obj["choices"][0]["message"]["content"] or ""
            except (KeyError, IndexError, TypeError):
                pass

            llm_call_steps.append(LlmCallStep(
                id=lc.id,
                model=lc.model,
                call_index=lc.call_index,
                messages=_parse_json(lc.messages, []),
                response_content=response_content,
                input_tokens=lc.input_tokens,
                output_tokens=lc.output_tokens,
                cost_usd=lc.cost_usd,
                latency_ms=lc.latency_ms,
                finish_reason=lc.finish_reason,
                tool_calls=tool_steps,
            ))

        steps.append(NodeStep(
            id=nr.id,
            node_id=nr.node_id,
            node_name=nr.node_name,
            node_type=nr.node_type,
            status=nr.status,
            started_at=nr.started_at,
            completed_at=nr.completed_at,
            duration_ms=nr.duration_ms,
            cost_usd=nr.cost_usd,
            input_tokens=nr.input_tokens,
            output_tokens=nr.output_tokens,
            output_data=_parse_json(nr.output_data, None),
            error_message=nr.error_message,
            llm_calls=llm_call_steps,
        ))

    return RunReplay(
        run_id=run.id,
        workflow_id=run.workflow_id,
        status=run.status,
        trigger_type=run.trigger_type,
        input_data=_parse_json(run.input_data, None),
        output_data=_parse_json(run.output_data, None),
        error_message=run.error_message,
        started_at=run.started_at,
        completed_at=run.completed_at,
        duration_ms=run.duration_ms,
        total_cost_usd=run.total_cost_usd,
        total_input_tokens=run.total_input_tokens,
        total_output_tokens=run.total_output_tokens,
        steps=steps,
    )


def _parse_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default
