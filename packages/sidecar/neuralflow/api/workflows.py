import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
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
    WorkspaceUpdate,
    WorkspaceExport,
)

router = APIRouter(prefix="/api")


# ── Workspaces ──────────────────────────────────────────────────────────────

@router.get("/workspaces", response_model=list[WorkspaceOut])
async def list_workspaces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workspace).order_by(Workspace.created_at))
    return result.scalars().all()


@router.post("/workspaces", response_model=WorkspaceOut, status_code=201)
async def create_workspace(body: WorkspaceCreate, db: AsyncSession = Depends(get_db)):
    settings_json = None
    if body.settings:
        settings_json = json.dumps(body.settings)
    ws = Workspace(
        id=str(uuid.uuid4()),
        name=body.name,
        description=body.description,
        settings=settings_json,
    )
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


@router.patch("/workspaces/{ws_id}", response_model=WorkspaceOut)
async def update_workspace(ws_id: str, body: WorkspaceUpdate, db: AsyncSession = Depends(get_db)):
    ws = await db.get(Workspace, ws_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    if body.name is not None:
        ws.name = body.name
    if body.description is not None:
        ws.description = body.description
    if body.settings is not None:
        ws.settings = json.dumps(body.settings)
    await db.commit()
    await db.refresh(ws)
    return ws


@router.delete("/workspaces/{ws_id}", status_code=204)
async def delete_workspace(ws_id: str, db: AsyncSession = Depends(get_db)):
    ws = await db.get(Workspace, ws_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")
    await db.delete(ws)
    await db.commit()


@router.get("/workspaces/{ws_id}/export")
async def export_workspace(ws_id: str, db: AsyncSession = Depends(get_db)):
    """Export a workspace as a JSON file containing settings and all workflows."""
    ws = await db.get(Workspace, ws_id)
    if not ws:
        raise HTTPException(404, "Workspace not found")

    result = await db.execute(
        select(Workflow).where(Workflow.workspace_id == ws_id).order_by(Workflow.created_at)
    )
    workflows = result.scalars().all()

    settings = json.loads(ws.settings) if ws.settings else {}
    export_data = WorkspaceExport(
        workspace_name=ws.name,
        workspace_description=ws.description,
        settings=settings,
        workflows=[
            {
                "name": wf.name,
                "description": wf.description,
                "tags": json.loads(wf.tags) if wf.tags else [],
                "canvas_data": json.loads(wf.canvas_data) if isinstance(wf.canvas_data, str) else wf.canvas_data,
                "execution_mode": wf.execution_mode,
            }
            for wf in workflows
        ],
    )

    content = json.dumps(export_data.model_dump(), indent=2)

    async def iter_content():
        yield content

    return StreamingResponse(
        iter_content(),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{ws.name.replace(" ", "_")}.json"'},
    )


@router.post("/workspaces/import", response_model=WorkspaceOut, status_code=201)
async def import_workspace(body: WorkspaceExport, db: AsyncSession = Depends(get_db)):
    """Import a workspace from an exported JSON structure."""
    ws = Workspace(
        id=str(uuid.uuid4()),
        name=body.workspace_name,
        description=body.workspace_description,
        settings=json.dumps(body.settings) if body.settings else None,
    )
    db.add(ws)
    await db.commit()
    await db.refresh(ws)

    # Import workflows
    for wf_data in body.workflows:
        wf = Workflow(
            id=str(uuid.uuid4()),
            workspace_id=ws.id,
            name=wf_data["name"],
            description=wf_data.get("description"),
            tags=json.dumps(wf_data.get("tags", [])),
            canvas_data=json.dumps(wf_data.get("canvas_data", {"nodes": [], "edges": []})),
            execution_mode=wf_data.get("execution_mode", "sequential"),
        )
        db.add(wf)

    await db.commit()
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
