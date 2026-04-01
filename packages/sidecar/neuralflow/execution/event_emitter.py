import asyncio
from typing import Any


class EventEmitter:
    """Pushes structured SSE events to the run's asyncio queue."""

    def __init__(self, run_id: str, queue: asyncio.Queue):
        self.run_id = run_id
        self._queue = queue

    async def emit(self, event_type: str, **payload: Any) -> None:
        await self._queue.put({"type": event_type, "run_id": self.run_id, **payload})

    async def run_started(self) -> None:
        await self.emit("run_started")

    async def run_completed(self, output: Any) -> None:
        await self.emit("run_completed", output=output)
        await self.emit("done")

    async def run_failed(self, error: str) -> None:
        await self.emit("run_failed", error=error)
        await self.emit("error", message=error)

    async def node_started(self, node_id: str, node_name: str, node_type: str) -> None:
        await self.emit("node_started", node_id=node_id, node_name=node_name, node_type=node_type)

    async def node_completed(self, node_id: str, output: Any, cost_usd: float = 0.0) -> None:
        await self.emit("node_completed", node_id=node_id, output=output, cost_usd=cost_usd)

    async def node_failed(self, node_id: str, error: str) -> None:
        await self.emit("node_failed", node_id=node_id, error=error)

    async def llm_chunk(self, node_id: str, chunk: str) -> None:
        await self.emit("llm_chunk", node_id=node_id, chunk=chunk)

    async def tool_call(self, node_id: str, tool_name: str, input_data: Any) -> None:
        await self.emit("tool_call", node_id=node_id, tool_name=tool_name, input=input_data)

    async def tool_result(self, node_id: str, tool_name: str, output: Any) -> None:
        await self.emit("tool_result", node_id=node_id, tool_name=tool_name, output=output)

    async def log(self, node_id: str, message: str, level: str = "info") -> None:
        await self.emit("log", node_id=node_id, message=message, level=level)
