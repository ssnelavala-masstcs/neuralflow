from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator
import json


class WorkflowCreate(BaseModel):
    workspace_id: str
    name: str
    description: str | None = None
    tags: list[str] = []
    canvas_data: dict[str, Any] = {"nodes": [], "edges": []}
    execution_mode: str = "sequential"
    is_template: bool = False


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    canvas_data: dict[str, Any] | None = None
    execution_mode: str | None = None


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


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None


class WorkspaceOut(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
