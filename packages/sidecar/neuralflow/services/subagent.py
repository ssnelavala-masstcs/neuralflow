"""Sub-agent spawning support for agent delegation."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("neuralflow.subagent")


@dataclass
class SubAgentConfig:
    """Configuration for a sub-agent."""

    name: str
    role: str
    system_prompt: str
    model: str
    max_iterations: int = 10
    max_tokens: int = 4096


@dataclass
class SubAgentResult:
    """Result from a sub-agent execution."""

    name: str
    success: bool
    output: str | None = None
    error: str | None = None
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    duration_ms: float = 0.0


class SubAgentManager:
    """Manages sub-agent spawning and execution."""

    def __init__(self) -> None:
        self._active: dict[str, SubAgentResult] = {}

    async def spawn(
        self,
        configs: list[SubAgentConfig],
        input_data: dict[str, Any],
        agent_runner,  # AgentRunner instance
    ) -> list[SubAgentResult]:
        """Spawn multiple sub-agents in parallel and collect results."""
        tasks = [
            self._run_single(cfg, input_data, agent_runner)
            for cfg in configs
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for cfg, result in zip(configs, results):
            if isinstance(result, Exception):
                final_results.append(SubAgentResult(
                    name=cfg.name,
                    success=False,
                    error=str(result),
                ))
            else:
                final_results.append(result)

        return final_results

    async def _run_single(
        self,
        config: SubAgentConfig,
        input_data: dict[str, Any],
        agent_runner,
    ) -> SubAgentResult:
        """Run a single sub-agent."""
        import time
        start = time.monotonic()

        try:
            logger.info("subagent_starting", extra={"name": config.name, "model": config.model})

            # Build messages from input
            messages = [
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": str(input_data)},
            ]

            # Run through agent runner
            result = await agent_runner.run_with_model(
                model=config.model,
                messages=messages,
                max_tokens=config.max_tokens,
                max_iterations=config.max_iterations,
            )

            duration_ms = (time.monotonic() - start) * 1000

            return SubAgentResult(
                name=config.name,
                success=True,
                output=result.get("output", ""),
                cost_usd=result.get("cost_usd", 0.0),
                input_tokens=result.get("input_tokens", 0),
                output_tokens=result.get("output_tokens", 0),
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            logger.exception("subagent_failed", extra={"name": config.name})
            return SubAgentResult(
                name=config.name,
                success=False,
                error=str(e),
                duration_ms=duration_ms,
            )


# Global singleton
subagent_manager = SubAgentManager()
