"""Top-level run orchestrator: loads run, dispatches to correct executor."""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.execution.event_emitter import EventEmitter
from neuralflow.execution.workflow_analyzer import analyze
from neuralflow.models.run import Run
from neuralflow.models.workflow import Workflow


class Orchestrator:
    def __init__(self, db: AsyncSession, run_id: str, event_queue: asyncio.Queue):
        self.db = db
        self.run_id = run_id
        self.emitter = EventEmitter(run_id=run_id, queue=event_queue)

    async def execute(self, workflow_id: str, input_data: dict[str, Any] | None) -> None:
        run = await self.db.get(Run, self.run_id)
        if not run:
            raise ValueError(f"Run {self.run_id} not found")

        wf = await self.db.get(Workflow, workflow_id)
        if not wf:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Mark run as started
        run.status = "running"
        run.started_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.emitter.run_started()

        start_ms = int(time.time() * 1000)

        try:
            canvas = json.loads(wf.canvas_data) if isinstance(wf.canvas_data, str) else wf.canvas_data
            workflow = analyze(canvas, execution_mode=wf.execution_mode)

            # Build provider key map from DB
            provider_key_map = await self._build_provider_key_map()

            # Dispatch to executor
            if wf.execution_mode in ("sequential", "parallel"):
                from neuralflow.execution.sequential_executor import SequentialExecutor
                executor = SequentialExecutor(db=self.db, run_id=self.run_id, emitter=self.emitter)
                result = await executor.execute(workflow, input_data, provider_key_map)
            else:
                # Phase 2: CrewAI / LangGraph — fall back to sequential for now
                from neuralflow.execution.sequential_executor import SequentialExecutor
                executor = SequentialExecutor(db=self.db, run_id=self.run_id, emitter=self.emitter)
                result = await executor.execute(workflow, input_data, provider_key_map)

            run.status = "complete"
            run.output_data = json.dumps(result)
            run.run_count = (run.run_count or 0) + 1

            # Roll up cost and token totals from node_runs
            await self._rollup_costs(run)

            run.completed_at = datetime.now(timezone.utc)
            run.duration_ms = int(time.time() * 1000) - start_ms

            # Update workflow metadata
            wf.last_run_at = run.completed_at
            wf.run_count = (wf.run_count or 0) + 1

            await self.db.commit()
            await self.emitter.run_completed(result.get("output"))

        except Exception as exc:
            run.status = "error"
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            run.duration_ms = int(time.time() * 1000) - start_ms
            await self.db.commit()
            await self.emitter.run_failed(str(exc))
            raise

    async def _build_provider_key_map(self) -> dict[str, tuple[str | None, str | None]]:
        """
        Returns mapping of provider_type → (api_key, base_url).
        API keys are stored in the OS keychain via Tauri IPC; here we just
        pass None for keys not configured, letting LiteLLM fall back to env vars.
        """
        from sqlalchemy import select
        from neuralflow.models.provider import Provider

        result = await self.db.execute(select(Provider).where(Provider.is_active == True))  # noqa: E712
        providers = result.scalars().all()
        key_map: dict[str, tuple[str | None, str | None]] = {}
        for p in providers:
            # api_key_ref is the keychain reference; actual key retrieval requires
            # Tauri IPC from the frontend. For now we check environment variables as fallback.
            import os
            env_key = os.environ.get(f"NEURALFLOW_KEY_{p.provider_type.upper()}")
            key_map[p.provider_type] = (env_key, p.base_url)
        return key_map

    async def _rollup_costs(self, run: Run) -> None:
        from sqlalchemy import select, func
        from neuralflow.models.run import NodeRun

        result = await self.db.execute(
            select(
                func.sum(NodeRun.cost_usd),
                func.sum(NodeRun.input_tokens),
                func.sum(NodeRun.output_tokens),
            ).where(NodeRun.run_id == run.id)
        )
        row = result.one()
        run.total_cost_usd = row[0] or 0.0
        run.total_input_tokens = row[1] or 0
        run.total_output_tokens = row[2] or 0
