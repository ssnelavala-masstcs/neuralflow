from datetime import datetime
from typing import Any

from pydantic import BaseModel


class McpServerCreate(BaseModel):
    name: str
    transport: str  # stdio | sse | http
    command: str | None = None
    args: list[str] = []
    url: str | None = None
    env_vars: dict[str, str] = {}
    headers: dict[str, str] = {}


class McpServerUpdate(BaseModel):
    name: str | None = None
    command: str | None = None
    args: list[str] | None = None
    url: str | None = None
    env_vars: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    is_active: bool | None = None


class McpServerOut(BaseModel):
    id: str
    name: str
    transport: str
    command: str | None
    args: list[str]
    url: str | None
    is_active: bool
    last_connected_at: datetime | None
    capabilities: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class McpToolOut(BaseModel):
    name: str
    description: str | None
    input_schema: dict[str, Any]
    server_id: str
    server_name: str
