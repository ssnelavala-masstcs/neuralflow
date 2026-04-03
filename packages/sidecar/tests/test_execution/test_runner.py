"""Tests for workflow CRUD and execution endpoints."""


class TestWorkflowCRUD:
    """Test workflow creation, listing, retrieval, update, and deletion."""

    async def test_create_workflow(self, client, workspace):
        ws_id = workspace.get("id")
        resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={
                "workspace_id": ws_id,
                "name": "my-first-workflow",
                "execution_mode": "sequential",
            },
        )
        assert resp.status_code in (200, 201), f"Body: {resp.text}"
        data = resp.json()
        assert data["name"] == "my-first-workflow"
        assert "id" in data

    async def test_list_workflows(self, client, workspace):
        ws_id = workspace.get("id")
        await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "list-test-wf", "execution_mode": "sequential"},
        )
        resp = await client.get(f"/api/workspaces/{ws_id}/workflows")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_workflow(self, client, workspace):
        ws_id = workspace.get("id")
        create_resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "get-test-wf", "execution_mode": "sequential"},
        )
        wf_id = create_resp.json()["id"]
        resp = await client.get(f"/api/workflows/{wf_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == wf_id
        assert data["name"] == "get-test-wf"

    async def test_update_workflow(self, client, workspace):
        ws_id = workspace.get("id")
        create_resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "update-test-wf", "execution_mode": "sequential"},
        )
        wf_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/api/workflows/{wf_id}",
            json={"name": "updated-workflow"},
        )
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == "updated-workflow"

    async def test_delete_workflow(self, client, workspace):
        ws_id = workspace.get("id")
        create_resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "delete-test-wf", "execution_mode": "sequential"},
        )
        wf_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/workflows/{wf_id}")
        assert resp.status_code in (200, 204)

    async def test_get_nonexistent_workflow_returns_404(self, client):
        resp = await client.get("/api/workflows/nonexistent-id")
        assert resp.status_code == 404


class TestWorkflowWithCanvas:
    """Test creating workflows with canvas data."""

    async def test_create_workflow_with_canvas_data(self, client, workspace):
        ws_id = workspace.get("id")
        resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={
                "workspace_id": ws_id,
                "name": "canvas-test-wf",
                "execution_mode": "sequential",
                "canvas_data": {
                    "nodes": [
                        {
                            "id": "input_1",
                            "type": "InputNode",
                            "position": {"x": 100, "y": 100},
                            "data": {"label": "Input"},
                        }
                    ],
                    "edges": [],
                },
            },
        )
        assert resp.status_code in (200, 201), f"Body: {resp.text}"
        data = resp.json()
        assert "canvas_data" in data


class TestExecutionModes:
    """Test that different execution modes are accepted."""

    async def test_sequential_mode(self, client, workspace):
        ws_id = workspace.get("id")
        resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "seq-wf", "execution_mode": "sequential"},
        )
        assert resp.status_code in (200, 201), f"Body: {resp.text}"

    async def test_hierarchical_mode(self, client, workspace):
        ws_id = workspace.get("id")
        resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "hier-wf", "execution_mode": "hierarchical"},
        )
        assert resp.status_code in (200, 201), f"Body: {resp.text}"

    async def test_state_machine_mode(self, client, workspace):
        ws_id = workspace.get("id")
        resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "sm-wf", "execution_mode": "state_machine"},
        )
        assert resp.status_code in (200, 201), f"Body: {resp.text}"

    async def test_auto_mode(self, client, workspace):
        ws_id = workspace.get("id")
        resp = await client.post(
            f"/api/workspaces/{ws_id}/workflows",
            json={"workspace_id": ws_id, "name": "auto-wf", "execution_mode": "auto"},
        )
        assert resp.status_code in (200, 201), f"Body: {resp.text}"


class TestRunEndpoints:
    """Test run listing (without actual execution)."""

    async def test_list_runs_empty(self, client):
        resp = await client.get("/api/runs")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
