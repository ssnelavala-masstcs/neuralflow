"""Shared test fixtures for the NeuralFlow sidecar.

Provides a test app with an isolated SQLite database, an AsyncClient,
and sample data factories.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from neuralflow.main import create_app
from neuralflow.database import init_db, make_engine, AsyncSessionLocal
import neuralflow.database as db_mod


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Path:
    """Return a temporary workspace directory."""
    ws = tmp_path / "neuralflow-test"
    ws.mkdir(parents=True, exist_ok=True)
    return ws


@pytest.fixture
async def app(tmp_workspace: Path):
    """Create a test app with an isolated SQLite database.

    testing=True skips the lifespan (no scheduler) and middleware
    (rate limiter, request size) for ASGI test client compatibility.
    """
    db_path = tmp_workspace / "test.db"

    with patch("neuralflow.config.settings") as mock_settings:
        mock_settings.workspace_dir = str(tmp_workspace)
        mock_settings.default_workspace_dir = str(tmp_workspace)
        mock_settings.host = "127.0.0.1"
        mock_settings.port = 7411
        mock_settings.log_level = "critical"
        mock_settings.auth_enabled = False
        mock_settings.cors_origins = ["http://localhost:1420"]

        with patch("neuralflow.database.settings", mock_settings):
            # Point engine at temp db
            db_mod.engine = make_engine(db_path)
            db_mod.AsyncSessionLocal = async_sessionmaker(
                db_mod.engine, expire_on_commit=False
            )

            application = create_app(testing=True)
            await init_db()

            yield application


from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest.fixture
async def client(app):
    """Async HTTP client for the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def workspace(client):
    """Create a test workspace and return its dict representation."""
    resp = await client.post("/api/workspaces", json={"name": "test-workspace"})
    assert resp.status_code in (200, 201, 409), f"Failed to create workspace: {resp.text}"
    data = resp.json()
    if isinstance(data, list):
        return data[0]
    return data


@pytest.fixture
async def workflow(client, workspace):
    """Create a test workflow and return its dict representation."""
    ws_id = workspace.get("id")
    resp = await client.post(
        f"/api/workspaces/{ws_id}/workflows",
        json={
            "name": "test-workflow",
            "execution_mode": "sequential",
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
    )
    assert resp.status_code in (200, 201), f"Failed to create workflow: {resp.text}"
    return resp.json()
