"""Memory/RAG endpoints: document ingestion, chunk search, CRUD."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db

router = APIRouter(prefix="/api/memory")


# ── Schemas ───────────────────────────────────────────────────────────────────

class MemoryChunkOut(BaseModel):
    id: str
    workflow_id: str
    node_id: str | None
    document_name: str
    chunk_index: int
    content: str
    created_at: Any

    model_config = {"from_attributes": True}


class MemorySearchResult(BaseModel):
    chunk: MemoryChunkOut
    score: float


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/ingest", response_model=list[MemoryChunkOut], status_code=201)
async def ingest_document(
    workflow_id: str = Query(...),
    node_id: str | None = Query(None),
    embedding_model: str | None = Query(None, description="LiteLLM embedding model, e.g. openai/text-embedding-3-small"),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document (TXT, MD, PDF, DOCX) and store chunked embeddings."""
    from neuralflow.memory.ingestion import ingest_file

    content_bytes = await file.read()
    filename = file.filename or "upload"
    try:
        chunks = await ingest_file(
            db=db,
            workflow_id=workflow_id,
            node_id=node_id,
            filename=filename,
            content_bytes=content_bytes,
            embedding_model=embedding_model,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    await db.commit()
    return chunks


@router.get("/search", response_model=list[MemorySearchResult])
async def search_memory(
    workflow_id: str = Query(...),
    query: str = Query(...),
    node_id: str | None = Query(None),
    top_k: int = Query(5, ge=1, le=50),
    embedding_model: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Semantic (or keyword fallback) search over stored memory chunks."""
    from neuralflow.memory.store import search

    results = await search(
        db=db,
        workflow_id=workflow_id,
        query=query,
        node_id=node_id,
        top_k=top_k,
        embedding_model=embedding_model,
    )
    return [MemorySearchResult(chunk=r[0], score=r[1]) for r in results]


@router.get("", response_model=list[MemoryChunkOut])
async def list_chunks(
    workflow_id: str = Query(...),
    node_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all memory chunks for a workflow (optionally filtered by node_id)."""
    from neuralflow.models.memory import MemoryChunk

    stmt = select(MemoryChunk).where(MemoryChunk.workflow_id == workflow_id)
    if node_id:
        stmt = stmt.where(MemoryChunk.node_id == node_id)
    stmt = stmt.order_by(MemoryChunk.document_name, MemoryChunk.chunk_index)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.delete("", status_code=200)
async def delete_chunks(
    workflow_id: str = Query(...),
    node_id: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete all memory chunks for a workflow (optionally scoped to a node)."""
    from neuralflow.memory.store import delete_chunks

    count = await delete_chunks(db=db, workflow_id=workflow_id, node_id=node_id)
    await db.commit()
    return {"deleted": count}
