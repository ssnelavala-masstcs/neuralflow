"""MCP connection pool — manages stdio and HTTP MCP server connections."""
from __future__ import annotations

import asyncio
import json
from typing import Any

from neuralflow.models.mcp_server import McpServer


class McpConnectionPool:
    """Singleton-style pool keyed by server ID."""

    def __init__(self):
        self._sessions: dict[str, Any] = {}  # server_id → mcp.ClientSession

    async def connect(self, server: McpServer) -> list[dict]:
        """Connect to an MCP server and return its tool list."""
        try:
            if server.transport == "stdio":
                return await self._connect_stdio(server)
            elif server.transport in ("sse", "http"):
                return await self._connect_http(server)
            else:
                raise ValueError(f"Unsupported MCP transport: {server.transport}")
        except Exception as exc:
            raise RuntimeError(f"Failed to connect to MCP server '{server.name}': {exc}") from exc

    async def _connect_stdio(self, server: McpServer) -> list[dict]:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        command = server.command
        args = json.loads(server.args) if server.args else []
        env = json.loads(server.env_vars) if server.env_vars else None

        params = StdioServerParameters(command=command, args=args, env=env)
        read, write = await stdio_client(params).__aenter__()
        session = await ClientSession(read, write).__aenter__()
        await session.initialize()

        self._sessions[server.id] = session
        tools_result = await session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema if hasattr(t, "inputSchema") else {},
            }
            for t in tools_result.tools
        ]

    async def _connect_http(self, server: McpServer) -> list[dict]:
        from mcp import ClientSession
        from mcp.client.sse import sse_client

        url = server.url
        headers = json.loads(server.headers) if server.headers else {}

        read, write = await sse_client(url, headers=headers).__aenter__()
        session = await ClientSession(read, write).__aenter__()
        await session.initialize()

        self._sessions[server.id] = session
        tools_result = await session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema if hasattr(t, "inputSchema") else {},
            }
            for t in tools_result.tools
        ]

    async def call_tool(self, server_id: str, tool_name: str, arguments: dict) -> Any:
        session = self._sessions.get(server_id)
        if session is None:
            raise RuntimeError(f"No active session for MCP server {server_id}")
        result = await session.call_tool(tool_name, arguments=arguments)
        return result.content

    async def disconnect(self, server_id: str) -> None:
        session = self._sessions.pop(server_id, None)
        if session:
            try:
                await session.__aexit__(None, None, None)
            except Exception:
                pass

    async def disconnect_all(self) -> None:
        for sid in list(self._sessions.keys()):
            await self.disconnect(sid)


# Module-level singleton
pool = McpConnectionPool()
