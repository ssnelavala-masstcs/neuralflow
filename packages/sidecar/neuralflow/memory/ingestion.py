from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.memory.store import add_chunk
from neuralflow.models.memory import MemoryChunk

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100


def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def _extract_text(filename: str, content_bytes: bytes) -> str:
    ext = Path(filename).suffix.lower()

    if ext in (".txt", ".md"):
        return content_bytes.decode("utf-8", errors="replace")

    if ext == ".pdf":
        try:
            import io
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("pypdf is required to ingest PDF files. Install it with: pip install pypdf")
        reader = PdfReader(io.BytesIO(content_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        try:
            import io
            from docx import Document
        except ImportError:
            raise RuntimeError(
                "python-docx is required to ingest DOCX files. Install it with: pip install python-docx"
            )
        doc = Document(io.BytesIO(content_bytes))
        return "\n".join(para.text for para in doc.paragraphs)

    raise ValueError(f"Unsupported file type: {ext!r}. Supported: .txt, .md, .pdf, .docx")


async def ingest_file(
    db: AsyncSession,
    workflow_id: str,
    node_id: Optional[str],
    filename: str,
    content_bytes: bytes,
    embedding_model: Optional[str] = None,
) -> list[MemoryChunk]:
    text = _extract_text(filename, content_bytes)
    raw_chunks = _split_text(text)

    results: list[MemoryChunk] = []
    for index, chunk_text in enumerate(raw_chunks):
        chunk_text = chunk_text.strip()
        if not chunk_text:
            continue
        chunk = await add_chunk(
            db=db,
            workflow_id=workflow_id,
            node_id=node_id,
            document_name=filename,
            chunk_index=index,
            content=chunk_text,
            embedding_model=embedding_model,
        )
        results.append(chunk)

    return results
