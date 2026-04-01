"""Simple sequential executor: runs agent nodes in topological order."""
from __future__ import annotations

import json
import time
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.execution.agent_runner import AgentRunner
from neuralflow.execution.event_emitter import EventEmitter
from neuralflow.execution.workflow_analyzer import AnalyzedWorkflow, NodeSpec
from neuralflow.models.run import NodeRun


class SequentialExecutor:
    def __init__(self, db: AsyncSession, run_id: str, emitter: EventEmitter):
        self.db = db
        self.run_id = run_id
        self.emitter = emitter

    async def execute(
        self,
        workflow: AnalyzedWorkflow,
        input_data: dict[str, Any] | None,
        provider_key_map: dict[str, tuple[str | None, str | None]],
    ) -> dict[str, Any]:
        """
        Run nodes in topological order.
        Returns the output of the last Output node, or the last agent output.
        """
        node_map = {n.id: n for n in workflow.nodes}
        # node_id → output produced by that node
        outputs: dict[str, Any] = {}
        final_output: Any = None

        initial_messages = _build_initial_messages(input_data)

        for node_id in workflow.topo_order:
            node = node_map.get(node_id)
            if node is None:
                continue

            if node.type == "trigger":
                outputs[node_id] = input_data
                continue

            if node.type == "output":
                # Collect predecessor outputs and surface them
                pred_outputs = [outputs.get(pid) for pid in workflow.predecessors.get(node_id, [])]
                final_output = pred_outputs[-1] if pred_outputs else None
                outputs[node_id] = final_output
                continue

            if node.type == "agent":
                node_run = await _create_node_run(self.db, node, self.run_id)
                await self.emitter.node_started(node.id, node.name, node.type)

                # Build messages: system prompt is in node data; user content is predecessor output
                pred_outputs = [outputs.get(pid) for pid in workflow.predecessors.get(node_id, [])]
                messages = _build_agent_messages(initial_messages, pred_outputs)

                # Look up provider API key
                model: str = node.data.get("model", "openai/gpt-4o-mini")
                provider_type = model.split("/")[0] if "/" in model else "openai"
                api_key, api_base = provider_key_map.get(provider_type, (None, None))

                # Gather tools assigned to this agent
                tools = await _resolve_agent_tools(node)

                start_ms = int(time.time() * 1000)
                try:
                    runner = AgentRunner(
                        db=self.db,
                        run_id=self.run_id,
                        node_run=node_run,
                        emitter=self.emitter,
                        api_key=api_key,
                        api_base=api_base,
                    )
                    result = await runner.run(node, messages, tools)
                    node_run.status = "complete"
                    node_run.output_data = json.dumps(result)
                    outputs[node_id] = result.get("output", "")
                    final_output = outputs[node_id]
                    await self.emitter.node_completed(node.id, outputs[node_id], result.get("cost_usd", 0.0))
                except Exception as exc:
                    node_run.status = "error"
                    node_run.error_message = str(exc)
                    await self.emitter.node_failed(node.id, str(exc))
                    raise
                finally:
                    node_run.duration_ms = int(time.time() * 1000) - start_ms
                    node_run.completed_at = _now()
                    await self.db.flush()
                continue

            # Unknown/unhandled node types — pass through
            outputs[node_id] = None

        return {"output": final_output}


def _build_initial_messages(input_data: dict | None) -> list[dict]:
    if not input_data:
        return []
    content = input_data.get("message") or json.dumps(input_data)
    return [{"role": "user", "content": content}]


def _build_agent_messages(initial: list[dict], pred_outputs: list[Any]) -> list[dict]:
    messages = list(initial)
    for out in pred_outputs:
        if out is None:
            continue
        content = out if isinstance(out, str) else json.dumps(out)
        # Inject predecessor output as a user turn if not already present
        if not messages or messages[-1].get("content") != content:
            messages.append({"role": "user", "content": content})
    return messages


async def _resolve_agent_tools(node: NodeSpec) -> list[dict]:
    """Convert tool names listed in node data to LiteLLM-compatible tool dicts."""
    from neuralflow.tools.registry import get_tool

    tool_names: list[str] = node.data.get("tools", [])
    tool_defs = []
    for name in tool_names:
        tool = get_tool(name)
        if tool:
            tool_defs.append(tool.to_litellm_tool())
    return tool_defs


async def _create_node_run(db_session, node: NodeSpec, run_id: str) -> NodeRun:
    nr = NodeRun(
        id=str(uuid.uuid4()),
        run_id=run_id,
        node_id=node.id,
        node_type=node.type,
        node_name=node.name,
        status="running",
        started_at=_now(),
    )
    db_session.add(nr)
    await db_session.flush()
    return nr


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
