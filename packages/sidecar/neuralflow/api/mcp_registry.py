"""MCP Registry API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from neuralflow.services.mcp_registry import mcp_registry

router = APIRouter(prefix="/api/mcp/registry")


@router.get("")
async def list_mcp_servers(
    category: str | None = Query(None),
) -> dict[str, Any]:
    """List all known MCP servers."""
    return {"servers": mcp_registry.list_all(category=category)}


@router.get("/categories")
async def list_categories() -> dict[str, Any]:
    """List all MCP server categories."""
    return {"categories": mcp_registry.categories()}


@router.get("/search")
async def search_mcp_servers(query: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Search MCP servers."""
    return {"servers": mcp_registry.search(query)}


@router.get("/{server_id}")
async def get_mcp_server(server_id: str) -> dict[str, Any]:
    """Get details for a specific MCP server."""
    server = mcp_registry.get(server_id)
    if not server:
        return {"error": "Server not found"}
    return {"server": server.to_dict()}
