import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.execution.code_exporter import CodeExporter
from neuralflow.execution.workflow_analyzer import analyze
from neuralflow.models.workflow import Workflow

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{workflow_id}/crewai")
async def export_crewai(workflow_id: str, db: AsyncSession = Depends(get_db)):
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    canvas_data = json.loads(workflow.canvas_data)
    analyzed = analyze(canvas_data, workflow.execution_mode)
    code = CodeExporter(analyzed).export_crewai()
    filename = f"{workflow.name}_crewai.py".replace(" ", "_")
    return JSONResponse({"code": code, "filename": filename})


@router.get("/{workflow_id}/langgraph")
async def export_langgraph(workflow_id: str, db: AsyncSession = Depends(get_db)):
    workflow = await db.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(404, "Workflow not found")
    canvas_data = json.loads(workflow.canvas_data)
    analyzed = analyze(canvas_data, workflow.execution_mode)
    code = CodeExporter(analyzed).export_langgraph()
    filename = f"{workflow.name}_langgraph.py".replace(" ", "_")
    return JSONResponse({"code": code, "filename": filename})
