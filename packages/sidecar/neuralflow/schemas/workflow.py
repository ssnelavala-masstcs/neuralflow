from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
import json


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    settings: dict[str, Any] | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    settings: dict[str, Any] | None = None


class WorkspaceOut(BaseModel):
    id: str
    name: str
    description: str | None
    settings: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, m: Any) -> "WorkspaceOut":
        settings = None
        if m.settings:
            try:
                settings = json.loads(m.settings) if isinstance(m.settings, str) else m.settings
            except (json.JSONDecodeError, TypeError):
                settings = None
        return cls(
            id=m.id,
            name=m.name,
            description=m.description,
            settings=settings,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class WorkspaceExport(BaseModel):
    """Schema for workspace export/import."""
    workspace_name: str
    workspace_description: str | None = None
    settings: dict[str, Any] | None = None
    workflows: list[dict[str, Any]] = []


class WorkflowCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    tags: list[str] = Field(default_factory=list)
    canvas_data: dict[str, Any] = Field(default_factory=lambda: {"nodes": [], "edges": []})
    execution_mode: str = Field(default="sequential", pattern=r"^[a-zA-Z0-9_-]+$")
    is_template: bool = False


class WorkflowUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    tags: list[str] | None = None
    canvas_data: dict[str, Any] | None = None
    execution_mode: str | None = Field(default=None, pattern=r"^[a-zA-Z0-9_-]+$")


class WorkflowOut(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str | None
    tags: list[str]
    canvas_data: dict[str, Any]
    execution_mode: str
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None
    run_count: int
    is_template: bool

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, m: Any) -> "WorkflowOut":
        tags = json.loads(m.tags) if m.tags else []
        canvas = json.loads(m.canvas_data) if isinstance(m.canvas_data, str) else m.canvas_data
        return cls(
            id=m.id,
            workspace_id=m.workspace_id,
            name=m.name,
            description=m.description,
            tags=tags,
            canvas_data=canvas,
            execution_mode=m.execution_mode,
            created_at=m.created_at,
            updated_at=m.updated_at,
            last_run_at=m.last_run_at,
            run_count=m.run_count,
            is_template=m.is_template,
        )
