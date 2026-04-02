import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.workflow import Workflow, WorkflowSnapshot
from neuralflow.schemas.workflow import WorkflowOut

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class SnapshotOut(BaseModel):
    id: str
    workflow_id: str
    snapshot_number: int
    canvas_data: dict[str, Any]
    change_summary: str | None
    created_at: datetime

    @classmethod
    def from_orm(cls, s: WorkflowSnapshot) -> "SnapshotOut":
        return cls(
            id=s.id,
            workflow_id=s.workflow_id,
            snapshot_number=s.snapshot_number,
            canvas_data=json.loads(s.canvas_data),
            change_summary=s.change_summary,
            created_at=s.created_at,
        )


class SnapshotCreate(BaseModel):
    workflow_id: str
    name: str | None = None


class SnapshotRename(BaseModel):
    name: str


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("", response_model=SnapshotOut, status_code=201)
async def create_snapshot(body: SnapshotCreate, db: AsyncSession = Depends(get_db)):
    workflow = await db.get(Workflow, body.workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")

    count_result = await db.execute(
        select(func.count()).where(WorkflowSnapshot.workflow_id == body.workflow_id)
    )
    next_number = (count_result.scalar() or 0) + 1

    snapshot = WorkflowSnapshot(
        id=str(uuid.uuid4()),
        workflow_id=body.workflow_id,
        snapshot_number=next_number,
        canvas_data=workflow.canvas_data,
        change_summary=body.name,
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)
    return SnapshotOut.from_orm(snapshot)


@router.get("", response_model=list[SnapshotOut])
async def list_snapshots(workflow_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkflowSnapshot)
        .where(WorkflowSnapshot.workflow_id == workflow_id)
        .order_by(WorkflowSnapshot.created_at.desc())
    )
    return [SnapshotOut.from_orm(s) for s in result.scalars().all()]


@router.get("/{snapshot_id}", response_model=SnapshotOut)
async def get_snapshot(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    snapshot = await db.get(WorkflowSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    return SnapshotOut.from_orm(snapshot)


@router.post("/{snapshot_id}/rollback")
async def rollback_snapshot(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    snapshot = await db.get(WorkflowSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    workflow = await db.get(Workflow, snapshot.workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    workflow.canvas_data = snapshot.canvas_data
    await db.commit()
    await db.refresh(workflow)
    return WorkflowOut.from_orm_model(workflow)


@router.patch("/{snapshot_id}/name", response_model=SnapshotOut)
async def rename_snapshot(snapshot_id: str, body: SnapshotRename, db: AsyncSession = Depends(get_db)):
    snapshot = await db.get(WorkflowSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    snapshot.change_summary = body.name
    await db.commit()
    await db.refresh(snapshot)
    return SnapshotOut.from_orm(snapshot)


@router.delete("/{snapshot_id}", status_code=204)
async def delete_snapshot(snapshot_id: str, db: AsyncSession = Depends(get_db)):
    snapshot = await db.get(WorkflowSnapshot, snapshot_id)
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    await db.delete(snapshot)
    await db.commit()
