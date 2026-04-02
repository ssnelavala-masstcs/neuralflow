"""LangGraph executor: builds a StateGraph from an AnalyzedWorkflow and streams execution."""
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

import litellm
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import TypedDict

from neuralflow.execution.event_emitter import EventEmitter
from neuralflow.execution.workflow_analyzer import AnalyzedWorkflow, NodeSpec
from neuralflow.models.run import NodeRun


class WorkflowState(TypedDict):
    messages: Annotated[list, add_messages]
    current_node_id: str
    outputs: dict[str, str]


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _create_node_run(db: AsyncSession, node: NodeSpec, run_id: str) -> NodeRun:
    nr = NodeRun(
        id=str(uuid.uuid4()),
        run_id=run_id,
        node_id=node.id,
        node_type=node.type,
        node_name=node.name,
        status="running",
        started_at=_now(),
    )
    db.add(nr)
    await db.flush()
    return nr


class LangGraphExecutor:
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
        node_map = {n.id: n for n in workflow.nodes}
        agent_nodes = [n for n in workflow.nodes if n.type == "agent"]
        node_runs: dict[str, NodeRun] = {}

        # Inject API keys into environment
        for provider_type, (api_key, _) in provider_key_map.items():
            if api_key:
                os.environ[f"{provider_type.upper()}_API_KEY"] = api_key

        # Build initial user message
        user_content = ""
        if input_data:
            user_content = input_data.get("message") or json.dumps(input_data)

        builder = StateGraph(WorkflowState)

        for node in agent_nodes:
            _node = node  # capture

            async def make_node_fn(n: NodeSpec):  # noqa: E306
                async def node_fn(state: WorkflowState) -> dict[str, Any]:
                    nr = node_runs.get(n.id)
                    if nr is None:
                        nr = await _create_node_run(self.db, n, self.run_id)
                        node_runs[n.id] = nr

                    await self.emitter.node_started(n.id, n.name, n.type)

                    # Build messages from state + system prompt
                    system_prompt = n.data.get("systemPrompt", "")
                    messages: list[dict] = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.extend(state["messages"])

                    model: str = n.data.get("model", "openai/gpt-4o-mini")
                    provider_type = model.split("/")[0] if "/" in model else "openai"
                    api_key, api_base = provider_key_map.get(provider_type, (None, None))

                    kwargs: dict[str, Any] = dict(
                        model=model,
                        messages=messages,
                        temperature=float(n.data.get("temperature", 0.7)),
                        max_tokens=int(n.data.get("maxTokens", 2048)),
                        stream=False,
                    )
                    if api_key:
                        kwargs["api_key"] = api_key
                    if api_base:
                        kwargs["api_base"] = api_base

                    start_ms = int(time.time() * 1000)
                    response = await litellm.acompletion(**kwargs)
                    output = response.choices[0].message.content or ""

                    cost_usd = 0.0
                    if response.usage:
                        nr.input_tokens = response.usage.prompt_tokens or 0
                        nr.output_tokens = response.usage.completion_tokens or 0
                        try:
                            cost_usd = litellm.completion_cost(completion_response=response)
                        except Exception:
                            cost_usd = 0.0

                    nr.status = "complete"
                    nr.output_data = json.dumps({"output": output})
                    nr.cost_usd = cost_usd
                    nr.duration_ms = int(time.time() * 1000) - start_ms
                    nr.completed_at = _now()
                    await self.db.flush()

                    await self.emitter.node_completed(n.id, output, cost_usd)

                    new_outputs = dict(state.get("outputs") or {})
                    new_outputs[n.id] = output
                    return {
                        "messages": [{"role": "assistant", "content": output}],
                        "current_node_id": n.id,
                        "outputs": new_outputs,
                    }

                return node_fn

            builder.add_node(_node.id, await make_node_fn(_node))

        # Determine entry point (first agent in topo order)
        entry_id: str | None = next(
            (nid for nid in workflow.topo_order if node_map.get(nid) and node_map[nid].type == "agent"),
            None,
        )
        if entry_id is None:
            return {"output": ""}

        builder.set_entry_point(entry_id)

        # Build set of all node IDs that are in the graph (agents only for now;
        # router nodes are handled by attaching their conditional logic to the
        # preceding agent node rather than as a separate graph node).
        agent_ids = {n.id for n in agent_nodes}
        # router_id → list of (condition, target_agent_id)
        router_conditions: dict[str, list[tuple[str, str]]] = {}
        for edge in workflow.edges:
            src = node_map.get(edge.source)
            if src and src.type == "router" and edge.target in agent_ids and edge.condition:
                router_conditions.setdefault(edge.source, []).append((edge.condition, edge.target))

        edges_added: set[str] = set()

        for edge in workflow.edges:
            # Skip edges that don't involve agent nodes on both ends; router edges
            # are handled separately below via their preceding agent nodes.
            if edge.source not in agent_ids:
                continue

            tgt_node = node_map.get(edge.target)
            if tgt_node and tgt_node.type == "router":
                # agent → router: attach conditional edges from this agent node
                r_conditions = router_conditions.get(edge.target, [])
                if r_conditions and edge.source not in edges_added:
                    def make_router(conditions: list[tuple[str, str]]):
                        def router_fn(state: WorkflowState) -> str:
                            for cond, tgt in conditions:
                                try:
                                    if eval(cond, {"outputs": state.get("outputs", {})}):  # noqa: S307
                                        return tgt
                                except Exception:
                                    pass
                            return END
                        return router_fn
                    builder.add_conditional_edges(edge.source, make_router(r_conditions))
                    edges_added.add(edge.source)
            elif edge.target in agent_ids and edge.source not in edges_added:
                builder.add_edge(edge.source, edge.target)
                edges_added.add(edge.source)

        # Nodes with no outgoing edges → END
        for node in agent_nodes:
            if node.id not in edges_added:
                builder.add_edge(node.id, END)

        saver = MemorySaver()
        graph = builder.compile(checkpointer=saver)

        initial_state: WorkflowState = {
            "messages": [{"role": "user", "content": user_content}] if user_content else [],
            "current_node_id": "",
            "outputs": {},
        }
        config = {"configurable": {"thread_id": self.run_id}}

        final_output = ""
        try:
            async for event in graph.astream(initial_state, config=config):
                for node_id, node_state in event.items():
                    if node_id == "__end__":
                        continue
                    outs = node_state.get("outputs") if isinstance(node_state, dict) else None
                    if outs:
                        last = list(outs.values())[-1]
                        if last:
                            final_output = last
        except Exception as exc:
            for nid, nr in node_runs.items():
                if nr.status == "running":
                    nr.status = "error"
                    nr.error_message = str(exc)
                    nr.completed_at = _now()
                    await self.emitter.node_failed(nid, str(exc))
            await self.db.flush()
            raise

        return {"output": final_output}
