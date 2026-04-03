import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.schemas.workflow import WorkflowOut

router = APIRouter(prefix="/api/templates")

# Templates dir relative to repo root — resolved at runtime
_TEMPLATES_DIR = Path(__file__).parents[4] / "templates"


@router.get("")
async def list_templates():
    templates = []
    for f in sorted(_TEMPLATES_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            templates.append({
                "file": f.name,
                "name": data.get("name", f.stem),
                "description": data.get("description", ""),
                "tags": data.get("tags", []),
            })
        except Exception:
            pass
    return templates


@router.post("/{filename}/import", response_model=WorkflowOut, status_code=201)
async def import_template(filename: str, workspace_id: str, db: AsyncSession = Depends(get_db)):
    path = _TEMPLATES_DIR / filename
    if not path.exists() or not path.suffix == ".json":
        raise HTTPException(404, "Template not found")

    from neuralflow.api.workflows import create_workflow
    from neuralflow.schemas.workflow import WorkflowCreate

    data = json.loads(path.read_text())
    body = WorkflowCreate(
        workspace_id=workspace_id,
        name=data.get("name", "Untitled"),
        description=data.get("description"),
        tags=data.get("tags", []),
        canvas_data=data.get("canvas_data", {"nodes": [], "edges": []}),
        execution_mode=data.get("execution_mode", "sequential"),
        is_template=False,
    )
    return await create_workflow(ws_id=workspace_id, body=body, db=db)
