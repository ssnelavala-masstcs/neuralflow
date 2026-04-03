"""MCP Server Registry — catalog of known MCP servers for discovery and install."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("neuralflow.mcp_registry")


@dataclass
class MCPServerEntry:
    id: str
    name: str
    description: str
    author: str
    transport: str  # stdio, sse, http
    command: str | None = None  # For stdio servers
    args: list[str] = field(default_factory=list)
    url: str | None = None  # For HTTP/SSE servers
    env_vars: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    category: str = "general"
    stars: int = 0
    install_count: int = 0
    homepage: str = ""
    repository: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "transport": self.transport,
            "command": self.command,
            "args": self.args,
            "url": self.url,
            "env_vars": self.env_vars,
            "tools": self.tools,
            "category": self.category,
            "stars": self.stars,
            "install_count": self.install_count,
            "homepage": self.homepage,
            "repository": self.repository,
        }


# Built-in MCP server catalog
_BUILTIN_SERVERS: list[MCPServerEntry] = [
    MCPServerEntry(
        id="filesystem",
        name="Filesystem",
        description="Read, write, and manage files on your system",
        author="Anthropic",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem"],
        category="development",
        tools=["read_file", "write_file", "list_directory"],
    ),
    MCPServerEntry(
        id="github",
        name="GitHub",
        description="Interact with GitHub repositories, issues, and PRs",
        author="Anthropic",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env_vars=["GITHUB_PERSONAL_ACCESS_TOKEN"],
        category="development",
        tools=["list_repos", "create_issue", "list_prs"],
    ),
    MCPServerEntry(
        id="slack",
        name="Slack",
        description="Send and receive Slack messages",
        author="Anthropic",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-slack"],
        env_vars=["SLACK_BOT_TOKEN", "SLACK_TEAM_ID"],
        category="communication",
        tools=["send_message", "list_channels"],
    ),
    MCPServerEntry(
        id="google-maps",
        name="Google Maps",
        description="Search places, get directions, and geocode addresses",
        author="Google",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-google-maps"],
        env_vars=["GOOGLE_MAPS_API_KEY"],
        category="utility",
        tools=["search_places", "get_directions", "geocode"],
    ),
    MCPServerEntry(
        id="fetch",
        name="Web Fetch",
        description="Fetch and parse web pages",
        author="Anthropic",
        transport="stdio",
        command="uvx",
        args=["mcp-server-fetch"],
        category="utility",
        tools=["fetch_url", "extract_content"],
    ),
    MCPServerEntry(
        id="postgres",
        name="PostgreSQL",
        description="Query PostgreSQL databases",
        author="Anthropic",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres"],
        category="database",
        tools=["query", "list_tables", "describe_table"],
    ),
    MCPServerEntry(
        id="sqlite",
        name="SQLite",
        description="Query SQLite databases",
        author="Anthropic",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-sqlite"],
        category="database",
        tools=["query", "list_tables"],
    ),
    MCPServerEntry(
        id="puppeteer",
        name="Puppeteer",
        description="Browser automation and web scraping",
        author="Anthropic",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-puppeteer"],
        category="development",
        tools=["navigate", "screenshot", "click", "evaluate"],
    ),
]


class MCPRegistry:
    """Registry of known MCP servers for discovery and install."""

    def __init__(self) -> None:
        self._servers: dict[str, MCPServerEntry] = {}
        for server in _BUILTIN_SERVERS:
            self._servers[server.id] = server

    def list_all(self, category: str | None = None) -> list[dict[str, Any]]:
        """List all registered MCP servers, optionally filtered by category."""
        servers = list(self._servers.values())
        if category:
            servers = [s for s in servers if s.category == category]
        return [s.to_dict() for s in sorted(servers, key=lambda s: s.name)]

    def get(self, server_id: str) -> MCPServerEntry | None:
        """Get a specific MCP server by ID."""
        return self._servers.get(server_id)

    def categories(self) -> list[str]:
        """List all available categories."""
        return sorted(set(s.category for s in self._servers.values()))

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search MCP servers by name or description."""
        q = query.lower()
        results = [
            s for s in self._servers.values()
            if q in s.name.lower() or q in s.description.lower() or q in " ".join(s.tools).lower()
        ]
        return [s.to_dict() for s in results]

    def register(self, server: MCPServerEntry) -> None:
        """Register a custom MCP server."""
        self._servers[server.id] = server


# Global singleton
mcp_registry = MCPRegistry()
