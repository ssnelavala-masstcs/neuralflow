import json
import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.workflow import Workflow
from neuralflow.schemas.workflow import WorkflowOut

router = APIRouter(prefix="/api/sharing")


class GistExportRequest(BaseModel):
    workflow_id: str
    gist_token: str
    public: bool = False


class GistExportResult(BaseModel):
    gist_url: str
    gist_id: str


class ImportUrlRequest(BaseModel):
    url: str
    workspace_id: str


COMMUNITY_TEMPLATES = [
    {
        "id": "ct-001",
        "name": "Multi-Agent Research",
        "description": "Parallel research agents that gather, synthesize, and summarize information from multiple sources.",
        "tags": ["research", "multi-agent", "parallel"],
        "gist_url": "https://gist.github.com/neuralflow/multi-agent-research",
        "thumbnail_url": None,
    },
    {
        "id": "ct-002",
        "name": "Customer Support Bot",
        "description": "Triage agent that routes tickets, drafts responses, and escalates unresolved issues.",
        "tags": ["support", "routing", "customer-service"],
        "gist_url": "https://gist.github.com/neuralflow/customer-support-bot",
        "thumbnail_url": None,
    },
    {
        "id": "ct-003",
        "name": "Code Review Pipeline",
        "description": "Automated code review with static analysis, security scan, and LLM commentary.",
        "tags": ["code-review", "security", "devtools"],
        "gist_url": "https://gist.github.com/neuralflow/code-review-pipeline",
        "thumbnail_url": None,
    },
    {
        "id": "ct-004",
        "name": "Data Analysis Crew",
        "description": "CrewAI crew that loads data, runs analysis, generates charts, and writes a report.",
        "tags": ["data", "analytics", "crewai"],
        "gist_url": "https://gist.github.com/neuralflow/data-analysis-crew",
        "thumbnail_url": None,
    },
    {
        "id": "ct-005",
        "name": "Content Generation Chain",
        "description": "Sequential chain: brief → outline → draft → edit → publish-ready article.",
        "tags": ["content", "writing", "sequential"],
        "gist_url": "https://gist.github.com/neuralflow/content-generation-chain",
        "thumbnail_url": None,
    },
]


@router.post("/export-gist", response_model=GistExportResult)
async def export_gist(body: GistExportRequest, db: AsyncSession = Depends(get_db)):
    wf = await db.get(Workflow, body.workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")

    canvas = json.loads(wf.canvas_data) if isinstance(wf.canvas_data, str) else wf.canvas_data
    gist_payload = {
        "description": f"NeuralFlow workflow: {wf.name}",
        "public": body.public,
        "files": {
            "neuralflow_workflow.json": {
                "content": json.dumps(canvas, indent=2),
            }
        },
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.github.com/gists",
            json=gist_payload,
            headers={
                "Authorization": f"token {body.gist_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15.0,
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(502, f"GitHub API error: {resp.text}")

    data = resp.json()
    return GistExportResult(gist_url=data["html_url"], gist_id=data["id"])


@router.post("/import-url", response_model=WorkflowOut)
async def import_url(body: ImportUrlRequest, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(body.url, timeout=15.0, follow_redirects=True)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(502, f"Failed to fetch URL: {exc}")

    try:
        canvas_data: dict[str, Any] = resp.json()
    except Exception:
        raise HTTPException(422, "URL did not return valid JSON")

    if "nodes" not in canvas_data or "edges" not in canvas_data:
        raise HTTPException(422, "JSON must have 'nodes' and 'edges' keys")

    wf = Workflow(
        id=str(uuid.uuid4()),
        workspace_id=body.workspace_id,
        name=canvas_data.get("name", "Imported Workflow"),
        description=canvas_data.get("description"),
        tags=json.dumps(canvas_data.get("tags", [])),
        canvas_data=json.dumps(canvas_data),
        execution_mode=canvas_data.get("execution_mode", "sequential"),
        is_template=False,
    )
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return WorkflowOut.from_orm_model(wf)


@router.get("/community-templates")
async def community_templates():
    return COMMUNITY_TEMPLATES
