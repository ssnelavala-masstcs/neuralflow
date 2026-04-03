"""Agent memory service — persistent context across runs."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("neuralflow.agent_memory")


@dataclass
class MemoryEntry:
    id: str
    agent_id: str
    content: str
    memory_type: str  # factual, procedural, conversational
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    relevance_score: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "content": self.content,
            "memory_type": self.memory_type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "relevance_score": self.relevance_score,
        }


class AgentMemoryService:
    """File-based agent memory with semantic search support."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._base = Path(base_dir or os.path.expanduser("~/.neuralflow/memory"))
        self._base.mkdir(parents=True, exist_ok=True)

    def _agent_dir(self, agent_id: str) -> Path:
        d = self._base / agent_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def add(
        self,
        agent_id: str,
        content: str,
        memory_type: str = "factual",
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """Add a memory entry for an agent."""
        import uuid
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            content=content,
            memory_type=memory_type,
            metadata=metadata or {},
        )
        path = self._agent_dir(agent_id) / f"{entry.id}.json"
        path.write_text(json.dumps(entry.to_dict()))
        logger.debug("memory_added", extra={"agent_id": agent_id, "memory_id": entry.id})
        return entry

    def search(
        self,
        agent_id: str,
        query: str | None = None,
        memory_type: str | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search memories for an agent."""
        agent_dir = self._agent_dir(agent_id)
        entries = []

        for path in agent_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                entry = MemoryEntry(**data)

                # Filter by type
                if memory_type and entry.memory_type != memory_type:
                    continue

                # Simple text matching for search (embeddings would be better)
                if query:
                    query_lower = query.lower()
                    if query_lower not in entry.content.lower():
                        continue

                entries.append(entry)
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by relevance score and creation time
        entries.sort(key=lambda e: e.relevance_score * e.created_at, reverse=True)
        return entries[:limit]

    def delete(self, agent_id: str, memory_id: str) -> bool:
        """Delete a specific memory."""
        path = self._agent_dir(agent_id) / f"{memory_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def list_agents(self) -> list[str]:
        """List all agents with memories."""
        return [d.name for d in self._base.iterdir() if d.is_dir()]

    def get_stats(self, agent_id: str) -> dict[str, Any]:
        """Get memory statistics for an agent."""
        agent_dir = self._agent_dir(agent_id)
        entries = []
        for path in agent_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                entries.append(data)
            except (json.JSONDecodeError, KeyError):
                continue

        type_counts: dict[str, int] = {}
        for e in entries:
            t = e.get("memory_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "total_memories": len(entries),
            "by_type": type_counts,
            "oldest": min((e.get("created_at", 0) for e in entries), default=0),
            "newest": max((e.get("created_at", 0) for e in entries), default=0),
        }


# Global singleton
agent_memory = AgentMemoryService()
