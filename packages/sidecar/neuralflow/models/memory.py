from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from neuralflow.database import Base


class MemoryChunk(Base):
    __tablename__ = "memory_chunks"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(Text, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    node_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_name: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON float array
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
