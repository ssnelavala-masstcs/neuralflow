"""Agent memory API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from neuralflow.services.agent_memory import agent_memory

router = APIRouter(prefix="/api/memory/agent")


@router.get("/{agent_id}")
async def get_agent_memories(
    agent_id: str,
    query: str | None = Query(None),
    memory_type: str | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
) -> dict[str, Any]:
    """Search memories for a specific agent."""
    entries = agent_memory.search(agent_id, query=query, memory_type=memory_type, limit=limit)
    return {"memories": [e.to_dict() for e in entries]}


@router.post("/{agent_id}")
async def add_agent_memory(
    agent_id: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    """Add a memory entry for an agent."""
    entry = agent_memory.add(
        agent_id=agent_id,
        content=body.get("content", ""),
        memory_type=body.get("memory_type", "factual"),
        metadata=body.get("metadata"),
    )
    return {"memory": entry.to_dict()}


@router.delete("/{agent_id}/{memory_id}")
async def delete_agent_memory(
    agent_id: str,
    memory_id: str,
) -> dict[str, Any]:
    """Delete a specific memory."""
    deleted = agent_memory.delete(agent_id, memory_id)
    return {"deleted": deleted}


@router.get("/{agent_id}/stats")
async def get_agent_memory_stats(agent_id: str) -> dict[str, Any]:
    """Get memory statistics for an agent."""
    return agent_memory.get_stats(agent_id)


@router.get("")
async def list_agent_memories() -> dict[str, Any]:
    """List all agents with memories."""
    agents = agent_memory.list_agents()
    return {"agents": agents}
