from __future__ import annotations

import json
import math
import uuid
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.models.memory import MemoryChunk


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)


async def _embed(text: str, embedding_model: str) -> list[float] | None:
    try:
        import litellm
        response = await litellm.aembedding(model=embedding_model, input=[text])
        return response.data[0]["embedding"]
    except Exception:
        return None


async def add_chunk(
    db: AsyncSession,
    workflow_id: str,
    node_id: Optional[str],
    document_name: str,
    chunk_index: int,
    content: str,
    embedding_model: Optional[str] = None,
) -> MemoryChunk:
    embedding_json: Optional[str] = None
    if embedding_model:
        vec = await _embed(content, embedding_model)
        if vec is not None:
            embedding_json = json.dumps(vec)

    chunk = MemoryChunk(
        id=str(uuid.uuid4()),
        workflow_id=workflow_id,
        node_id=node_id,
        document_name=document_name,
        chunk_index=chunk_index,
        content=content,
        embedding=embedding_json,
    )
    db.add(chunk)
    await db.flush()
    return chunk


async def search(
    db: AsyncSession,
    workflow_id: str,
    query: str,
    node_id: Optional[str] = None,
    top_k: int = 5,
    embedding_model: Optional[str] = None,
) -> list[tuple[MemoryChunk, float]]:
    """Returns list of (chunk, score) tuples ordered by relevance descending."""
    stmt = select(MemoryChunk).where(MemoryChunk.workflow_id == workflow_id)
    if node_id is not None:
        stmt = stmt.where(MemoryChunk.node_id == node_id)

    result = await db.execute(stmt)
    chunks: list[MemoryChunk] = list(result.scalars().all())

    if not chunks:
        return []

    # Prefer embedding-based search if available
    query_vec: Optional[list[float]] = None
    if embedding_model:
        query_vec = await _embed(query, embedding_model)

    chunks_with_embeddings = [c for c in chunks if c.embedding is not None]

    if query_vec is not None and chunks_with_embeddings:
        scored: list[tuple[MemoryChunk, float]] = []
        for chunk in chunks_with_embeddings:
            vec = json.loads(chunk.embedding)  # type: ignore[arg-type]
            score = cosine_similarity(query_vec, vec)
            scored.append((chunk, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    # Keyword fallback
    query_lower = query.lower()
    keyword_scored: list[tuple[MemoryChunk, float]] = []
    for chunk in chunks:
        score = float(chunk.content.lower().count(query_lower))
        keyword_scored.append((chunk, score))
    keyword_scored.sort(key=lambda x: x[1], reverse=True)
    top = keyword_scored[:top_k]
    hits = [(c, s) for c, s in top if s > 0]
    return hits if hits else top


async def delete_chunks(
    db: AsyncSession,
    workflow_id: str,
    node_id: Optional[str] = None,
) -> int:
    stmt = delete(MemoryChunk).where(MemoryChunk.workflow_id == workflow_id)
    if node_id is not None:
        stmt = stmt.where(MemoryChunk.node_id == node_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount  # type: ignore[return-value]
