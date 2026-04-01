import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.mcp.manager import pool
from neuralflow.models.mcp_server import McpServer
from neuralflow.schemas.mcp import McpServerCreate, McpServerOut, McpServerUpdate, McpToolOut

router = APIRouter(prefix="/api/mcp")


@router.get("/servers", response_model=list[McpServerOut])
async def list_servers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(McpServer).order_by(McpServer.created_at))
    servers = result.scalars().all()
    return [_to_out(s) for s in servers]


@router.post("/servers", response_model=McpServerOut, status_code=201)
async def add_server(body: McpServerCreate, db: AsyncSession = Depends(get_db)):
    s = McpServer(
        id=str(uuid.uuid4()),
        name=body.name,
        transport=body.transport,
        command=body.command,
        args=json.dumps(body.args),
        url=body.url,
        env_vars=json.dumps(body.env_vars),
        headers=json.dumps(body.headers),
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return _to_out(s)


@router.get("/servers/{server_id}", response_model=McpServerOut)
async def get_server(server_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(McpServer, server_id)
    if not s:
        raise HTTPException(404, "MCP server not found")
    return _to_out(s)


@router.patch("/servers/{server_id}", response_model=McpServerOut)
async def update_server(server_id: str, body: McpServerUpdate, db: AsyncSession = Depends(get_db)):
    s = await db.get(McpServer, server_id)
    if not s:
        raise HTTPException(404, "MCP server not found")
    if body.name is not None:
        s.name = body.name
    if body.command is not None:
        s.command = body.command
    if body.args is not None:
        s.args = json.dumps(body.args)
    if body.url is not None:
        s.url = body.url
    if body.env_vars is not None:
        s.env_vars = json.dumps(body.env_vars)
    if body.headers is not None:
        s.headers = json.dumps(body.headers)
    if body.is_active is not None:
        s.is_active = body.is_active
    await db.commit()
    await db.refresh(s)
    return _to_out(s)


@router.delete("/servers/{server_id}", status_code=204)
async def delete_server(server_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(McpServer, server_id)
    if not s:
        raise HTTPException(404, "MCP server not found")
    await pool.disconnect(server_id)
    await db.delete(s)
    await db.commit()


@router.post("/servers/{server_id}/connect", response_model=list[McpToolOut])
async def connect_server(server_id: str, db: AsyncSession = Depends(get_db)):
    s = await db.get(McpServer, server_id)
    if not s:
        raise HTTPException(404, "MCP server not found")
    tools_raw = await pool.connect(s)
    s.last_connected_at = datetime.now(timezone.utc)
    s.capabilities = json.dumps({"tools": [t["name"] for t in tools_raw]})
    await db.commit()
    return [
        McpToolOut(
            name=t["name"],
            description=t.get("description"),
            input_schema=t.get("input_schema", {}),
            server_id=s.id,
            server_name=s.name,
        )
        for t in tools_raw
    ]


def _to_out(s: McpServer) -> McpServerOut:
    return McpServerOut(
        id=s.id,
        name=s.name,
        transport=s.transport,
        command=s.command,
        args=json.loads(s.args) if s.args else [],
        url=s.url,
        is_active=s.is_active,
        last_connected_at=s.last_connected_at,
        capabilities=json.loads(s.capabilities) if s.capabilities else None,
        created_at=s.created_at,
    )
