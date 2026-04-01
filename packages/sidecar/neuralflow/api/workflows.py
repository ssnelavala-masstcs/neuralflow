import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.workspace import Workspace
from neuralflow.models.workflow import Workflow
from neuralflow.schemas.workflow import (
    WorkflowCreate,
    WorkflowOut,
    WorkflowUpdate,
    WorkspaceCreate,
    WorkspaceOut,
)

router = APIRouter(prefix="/api")


# ── Workspaces ──────────────────────────────────────────────────────────────

@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).order_by(Workspace.created_at))
    return result.scalars().all()


@router.post("/workspaces", response_model=WorkspaceOut, status_code=201)
async def create_workspace(body: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    ws = Workspace(id=str(uuid.uuid4()), name=body.name, description=body.description)
    db.add(ws)
    await db.commit()
    await db.refresh(ws)
    return ws


@router.get("/workspaces/{ws_id}", response_model=WorkspaceOut)
async def get_workspace(ws_id: str, db: AsyncSession = Depends(get_db)):
    ws = await db.get(Workspace, ws_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    return ws


# ── Workflows ────────────────────────────────────────────────────────────────

@router.get("/workspaces/{ws_id}/workflows", response_model=list[WorkflowOut])
async def list_workflows(ws_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Workflow).where(Workflow.workspace_id == ws_id).order_by(Workflow.updated_at.desc())
    )
    workflows = result.scalars().all()
    return [WorkflowOut.from_orm_model(w) for w in workflows]


@router.post("/workspaces/{ws_id}/workflows", response_model=WorkflowOut, status_code=201)
async def create_workflow(ws_id: str, body: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    ws = await db.get(Workspace, ws_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    wf = Workflow(
        id=str(uuid.uuid4()),
        workspace_id=ws_id,
        name=body.name,
        description=body.description,
        tags=json.dumps(body.tags),
        canvas_data=json.dumps(body.canvas_data),
        execution_mode=body.execution_mode,
        is_template=body.is_template,
    )
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return WorkflowOut.from_orm_model(wf)


@router.get("/workflows/{wf_id}", response_model=WorkflowOut)
async def get_workflow(wf_id: str, db: AsyncSession = Depends(get_db)):
    wf = await db.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    return WorkflowOut.from_orm_model(wf)


@router.patch("/workflows/{wf_id}", response_model=WorkflowOut)
async def update_workflow(wf_id: str, body: WorkflowUpdate, db: AsyncSession = Depends(get_db)):
    wf = await db.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    if body.name is not None:
        wf.name = body.name
    if body.description is not None:
        wf.description = body.description
    if body.tags is not None:
        wf.tags = json.dumps(body.tags)
    if body.canvas_data is not None:
        wf.canvas_data = json.dumps(body.canvas_data)
    if body.execution_mode is not None:
        wf.execution_mode = body.execution_mode
    await db.commit()
    await db.refresh(wf)
    return WorkflowOut.from_orm_model(wf)


@router.delete("/workflows/{wf_id}", status_code=204)
async def delete_workflow(wf_id: str, db: AsyncSession = Depends(get_db)):
    wf = await db.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    await db.delete(wf)
    await db.commit()


@router.post("/workflows/{wf_id}/duplicate", response_model=WorkflowOut, status_code=201)
async def duplicate_workflow(wf_id: str, db: AsyncSession = Depends(get_db)):
    wf = await db.get(Workflow, wf_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    tags = json.loads(wf.tags) if wf.tags else []
    new_wf = Workflow(
        id=str(uuid.uuid4()),
        workspace_id=wf.workspace_id,
        name=f"{wf.name} (copy)",
        description=wf.description,
        tags=json.dumps(tags),
        canvas_data=wf.canvas_data,
        execution_mode=wf.execution_mode,
        is_template=False,
    )
    db.add(new_wf)
    await db.commit()
    await db.refresh(new_wf)
    return WorkflowOut.from_orm_model(new_wf)
