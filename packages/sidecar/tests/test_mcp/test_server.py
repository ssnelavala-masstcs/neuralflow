"""Tests for MCP server management endpoints."""


class TestMCPServers:
    """Test MCP server CRUD operations."""

    async def test_list_mcp_servers_empty(self, client):
        resp = await client.get("/api/mcp/servers")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_create_stdio_mcp_server(self, client):
        resp = await client.post(
            "/api/mcp/servers",
            json={
                "name": "test-filesystem",
                "transport": "stdio",
                "command": "npx -y @modelcontextprotocol/server-filesystem /tmp",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "test-filesystem"
        assert data["transport"] == "stdio"

    async def test_create_sse_mcp_server(self, client):
        resp = await client.post(
            "/api/mcp/servers",
            json={
                "name": "test-sse-mcp",
                "transport": "sse",
                "url": "http://localhost:8080/sse",
            },
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "test-sse-mcp"
        assert data["transport"] == "sse"

    async def test_get_mcp_server(self, client):
        create_resp = await client.post(
            "/api/mcp/servers",
            json={
                "name": "get-test-mcp",
                "transport": "stdio",
                "command": "echo test",
            },
        )
        server_id = create_resp.json()["id"]
        resp = await client.get(f"/api/mcp/servers/{server_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == server_id

    async def test_delete_mcp_server(self, client):
        create_resp = await client.post(
            "/api/mcp/servers",
            json={
                "name": "delete-test-mcp",
                "transport": "stdio",
                "command": "echo test",
            },
        )
        server_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/mcp/servers/{server_id}")
        assert resp.status_code in (200, 204)

    async def test_get_nonexistent_mcp_server_returns_404(self, client):
        resp = await client.get("/api/mcp/servers/nonexistent-id")
        assert resp.status_code == 404


class TestMCPValidation:
    """Test MCP server input validation."""

    async def test_mcp_server_requires_name(self, client):
        resp = await client.post(
            "/api/mcp/servers",
            json={"transport": "stdio", "command": "echo test"},
        )
        assert resp.status_code == 422

    async def test_mcp_server_requires_transport(self, client):
        resp = await client.post(
            "/api/mcp/servers",
            json={"name": "test"},
        )
        assert resp.status_code == 422
