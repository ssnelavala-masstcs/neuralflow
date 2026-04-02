"""CrewAI executor: translates AnalyzedWorkflow into a CrewAI Crew and runs it."""
from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.execution.event_emitter import EventEmitter
from neuralflow.execution.workflow_analyzer import AnalyzedWorkflow, NodeSpec
from neuralflow.models.run import NodeRun


class CrewAIExecutor:
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
        from crewai import Agent, Crew, Process, Task

        agent_nodes = [n for n in workflow.nodes if n.type == "agent"]
        task_nodes = [n for n in workflow.nodes if n.type == "task"]

        if not agent_nodes:
            return {"output": None}

        # Inject API keys into environment so LiteLLM inside CrewAI can find them
        import os
        for provider_type, (api_key, api_base) in provider_key_map.items():
            if api_key:
                os.environ[f"{provider_type.upper()}_API_KEY"] = api_key

        # Build CrewAI agents and NodeRun DB records
        crew_agents: dict[str, Agent] = {}
        node_runs: dict[str, NodeRun] = {}

        for node in agent_nodes:
            model: str = node.data.get("model", "openai/gpt-4o-mini")
            agent = Agent(
                role=node.data.get("role") or node.name,
                goal=node.data.get("systemPrompt", "Complete the assigned task."),
                backstory=node.data.get("backstory", "An AI assistant built for this workflow."),
                llm=model,
                verbose=bool(node.data.get("verbose", True)),
                allow_delegation=bool(node.data.get("allowDelegation", False)),
                max_iter=int(node.data.get("maxIterations", 15)),
            )
            crew_agents[node.id] = agent

            nr = NodeRun(
                id=str(uuid.uuid4()),
                run_id=self.run_id,
                node_id=node.id,
                node_type=node.type,
                node_name=node.name,
                status="running",
                started_at=_now(),
            )
            self.db.add(nr)
            node_runs[node.id] = nr

        await self.db.flush()

        for node in agent_nodes:
            await self.emitter.node_started(node.id, node.name, node.type)

        # Build CrewAI tasks
        # If TaskNodes exist and are wired to agents, use them;
        # otherwise derive one task per agent from topological order.
        crew_tasks: list[Task] = []

        if task_nodes:
            for task_node in task_nodes:
                # Agent connected to this TaskNode (either direction)
                connected = [
                    e.target for e in workflow.edges if e.source == task_node.id and e.target in crew_agents
                ] + [
                    e.source for e in workflow.edges if e.target == task_node.id and e.source in crew_agents
                ]
                agent = crew_agents[connected[0]] if connected else next(iter(crew_agents.values()))
                crew_tasks.append(Task(
                    description=task_node.data.get("description", task_node.name),
                    expected_output=task_node.data.get("expectedOutput", "A complete and thorough response."),
                    agent=agent,
                ))
        else:
            user_input = _extract_input_text(input_data)
            agent_node_ids = [nid for nid in workflow.topo_order if nid in crew_agents]
            for i, nid in enumerate(agent_node_ids):
                node = next(n for n in agent_nodes if n.id == nid)
                desc = user_input if i == 0 else node.data.get("systemPrompt", "Continue from the previous agent and complete the task.")
                crew_tasks.append(Task(
                    description=desc or "Complete the task.",
                    expected_output="A thorough and complete response.",
                    agent=crew_agents[nid],
                ))

        # Detect hierarchical: an agent with allowDelegation=True acts as manager
        manager_agent: Agent | None = None
        for node in agent_nodes:
            if node.data.get("allowDelegation", False):
                manager_agent = crew_agents[node.id]
                break

        process = Process.hierarchical if manager_agent else Process.sequential

        crew_kwargs: dict[str, Any] = dict(
            agents=list(crew_agents.values()),
            tasks=crew_tasks,
            process=process,
            verbose=True,
        )
        if manager_agent:
            crew_kwargs["manager_agent"] = manager_agent

        crew = Crew(**crew_kwargs)

        # CrewAI kickoff is synchronous; run in thread executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        start_ms = int(time.time() * 1000)
        kickoff_inputs = {"input": _extract_input_text(input_data)} if input_data else {}

        try:
            crew_result = await loop.run_in_executor(
                None, lambda: crew.kickoff(inputs=kickoff_inputs)
            )
            final_output = str(crew_result.raw) if hasattr(crew_result, "raw") else str(crew_result)

            elapsed_ms = int(time.time() * 1000) - start_ms
            for node in agent_nodes:
                nr = node_runs[node.id]
                nr.status = "complete"
                nr.output_data = json.dumps({"output": final_output})
                nr.duration_ms = elapsed_ms
                nr.completed_at = _now()
                await self.emitter.node_completed(node.id, final_output, 0.0)

        except Exception as exc:
            elapsed_ms = int(time.time() * 1000) - start_ms
            for node in agent_nodes:
                nr = node_runs[node.id]
                nr.status = "error"
                nr.error_message = str(exc)
                nr.duration_ms = elapsed_ms
                nr.completed_at = _now()
                await self.emitter.node_failed(node.id, str(exc))
            await self.db.flush()
            raise

        await self.db.flush()
        return {"output": final_output}


def _extract_input_text(input_data: dict | None) -> str:
    if not input_data:
        return ""
    return input_data.get("message") or json.dumps(input_data)


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)
