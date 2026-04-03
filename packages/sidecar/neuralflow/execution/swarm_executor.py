"""Swarm executor — parallel worker agents for fan-out/replicate/specialize strategies."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("neuralflow.swarm")


class SwarmStrategy(str, Enum):
    FAN_OUT = "fan_out"       # Split input list across workers
    REPLICATE = "replicate"   # Same input to all workers, aggregate results
    SPECIALIZE = "specialize" # Each worker gets different system prompt


@dataclass
class SwarmWorker:
    id: str
    model: str
    system_prompt: str
    max_tokens: int = 4096


@dataclass
class SwarmResult:
    worker_id: str
    success: bool
    output: str | None = None
    error: str | None = None
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "cost_usd": round(self.cost_usd, 6),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "duration_ms": round(self.duration_ms, 2),
        }


class SwarmExecutor:
    """Execute agents in parallel with different strategies."""

    def __init__(self) -> None:
        self._active_swarms: dict[str, list[SwarmResult]] = {}

    async def execute(
        self,
        workers: list[SwarmWorker],
        inputs: list[dict[str, Any]],
        strategy: SwarmStrategy,
        agent_runner,
        aggregator: str = "concat",
    ) -> dict[str, Any]:
        """Execute a swarm and return aggregated results."""
        swarm_id = f"swarm-{int(time.time())}"
        tasks = self._build_tasks(workers, inputs, strategy, agent_runner)

        start = time.monotonic()
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        total_duration_ms = (time.monotonic() - start) * 1000

        results = []
        for worker, raw in zip(workers, raw_results):
            if isinstance(raw, Exception):
                result = SwarmResult(
                    worker_id=worker.id,
                    success=False,
                    error=str(raw),
                    duration_ms=total_duration_ms / len(workers),
                )
            else:
                result = SwarmResult(
                    worker_id=worker.id,
                    success=True,
                    **raw,
                    duration_ms=total_duration_ms / len(workers),
                )
            results.append(result)

        self._active_swarms[swarm_id] = results

        # Aggregate results
        aggregated = self._aggregate(results, aggregator)

        return {
            "swarm_id": swarm_id,
            "strategy": strategy.value,
            "total_workers": len(workers),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "total_cost_usd": round(sum(r.cost_usd for r in results), 6),
            "total_duration_ms": round(total_duration_ms, 2),
            "aggregated_output": aggregated,
            "per_worker": [r.to_dict() for r in results],
        }

    def _build_tasks(
        self,
        workers: list[SwarmWorker],
        inputs: list[dict[str, Any]],
        strategy: SwarmStrategy,
        agent_runner,
    ) -> list:
        """Build async tasks based on strategy."""
        tasks = []

        if strategy == SwarmStrategy.FAN_OUT:
            # Distribute inputs across workers
            for i, worker in enumerate(workers):
                worker_input = inputs[i % len(inputs)] if inputs else {}
                tasks.append(self._run_worker(worker, worker_input, agent_runner))

        elif strategy == SwarmStrategy.REPLICATE:
            # Same input to all workers
            for worker in workers:
                worker_input = inputs[0] if inputs else {}
                tasks.append(self._run_worker(worker, worker_input, agent_runner))

        elif strategy == SwarmStrategy.SPECIALIZE:
            # Each worker gets its own system prompt
            for i, worker in enumerate(workers):
                worker_input = inputs[i] if i < len(inputs) else {}
                tasks.append(self._run_worker(worker, worker_input, agent_runner))

        return tasks

    async def _run_worker(
        self,
        worker: SwarmWorker,
        input_data: dict[str, Any],
        agent_runner,
    ) -> dict[str, Any]:
        """Run a single swarm worker."""
        messages = [
            {"role": "system", "content": worker.system_prompt},
            {"role": "user", "content": str(input_data)},
        ]

        result = await agent_runner.run_with_model(
            model=worker.model,
            messages=messages,
            max_tokens=worker.max_tokens,
        )

        return {
            "output": result.get("output", ""),
            "cost_usd": result.get("cost_usd", 0.0),
            "input_tokens": result.get("input_tokens", 0),
            "output_tokens": result.get("output_tokens", 0),
        }

    def _aggregate(self, results: list[SwarmResult], strategy: str) -> str:
        """Aggregate worker results."""
        if strategy == "concat":
            return "\n\n---\n\n".join(
                f"Worker {r.worker_id}:\n{r.output}"
                for r in results if r.success
            )
        elif strategy == "json_merge":
            import json
            merged = {}
            for r in results:
                if r.success and r.output:
                    try:
                        merged[r.worker_id] = json.loads(r.output)
                    except json.JSONDecodeError:
                        merged[r.worker_id] = r.output
            return json.dumps(merged, indent=2)
        elif strategy == "last":
            successful = [r for r in results if r.success]
            return successful[-1].output if successful else ""
        else:
            return "\n\n".join(r.output or "" for r in results if r.success)

    def get_swarm_results(self, swarm_id: str) -> list[SwarmResult] | None:
        return self._active_swarms.get(swarm_id)


# Global singleton
swarm_executor = SwarmExecutor()
