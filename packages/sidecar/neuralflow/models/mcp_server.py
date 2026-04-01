import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from neuralflow.database import Base


class McpServer(Base):
    __tablename__ = "mcp_servers"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    transport: Mapped[str] = mapped_column(Text, nullable=False)  # stdio | sse | http
    command: Mapped[str | None] = mapped_column(Text)   # for stdio
    args: Mapped[str | None] = mapped_column(Text)      # JSON array, for stdio
    url: Mapped[str | None] = mapped_column(Text)       # for sse/http
    env_vars: Mapped[str | None] = mapped_column(Text)  # JSON
    headers: Mapped[str | None] = mapped_column(Text)   # JSON
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_connected_at: Mapped[datetime | None] = mapped_column(DateTime)
    capabilities: Mapped[str | None] = mapped_column(Text)  # JSON, cached
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
