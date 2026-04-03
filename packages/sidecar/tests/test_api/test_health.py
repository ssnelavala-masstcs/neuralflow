"""Tests for the health endpoint and basic API behavior."""


class TestHealthEndpoint:
    """Test GET /health."""

    async def test_health_returns_200(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "neuralflow-sidecar"

    async def test_health_has_required_fields(self, client):
        resp = await client.get("/health")
        data = resp.json()
        assert "status" in data
        assert "service" in data


class TestDocsEndpoint:
    """Test that Swagger UI is accessible."""

    async def test_docs_endpoint_exists(self, client):
        resp = await client.get("/docs")
        assert resp.status_code == 200


class TestToolsEndpoint:
    """Test GET /api/tools."""

    async def test_list_tools(self, client):
        resp = await client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Should have at least the built-in tools
        tool_names = [t["name"] for t in data]
        assert "web_search" in tool_names
        assert "file_read" in tool_names
        assert "file_write" in tool_names
        assert "http_request" in tool_names
        assert "calculator" in tool_names


class TestWorkspaceCRUD:
    """Test workspace creation, listing, and deletion."""

    async def test_create_workspace(self, client):
        resp = await client.post(
            "/api/workspaces",
            json={"name": "test-crud-workspace"},
        )
        assert resp.status_code in (200, 201, 409)

    async def test_list_workspaces(self, client):
        # Create one first
        await client.post("/api/workspaces", json={"name": "test-list-ws"})
        resp = await client.get("/api/workspaces")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_workspace_has_id(self, client):
        resp = await client.post("/api/workspaces", json={"name": "test-id-ws"})
        if resp.status_code in (200, 201):
            data = resp.json()
            assert "id" in data
        elif resp.status_code == 409:
            # Already exists — list and check
            resp = await client.get("/api/workspaces")
            data = resp.json()
            assert len(data) >= 1
            assert "id" in data[0]


class TestErrorHandling:
    """Test that errors return proper JSON format."""

    async def test_404_returns_json(self, client):
        resp = await client.get("/api/nonexistent")
        assert resp.status_code == 404
        data = resp.json()
        assert isinstance(data, dict)
        assert "error" in data or "detail" in data

    async def test_missing_required_field_returns_422(self, client):
        """Sending a workspace create with no name should fail validation."""
        resp = await client.post("/api/workspaces", json={})
        assert resp.status_code == 422
