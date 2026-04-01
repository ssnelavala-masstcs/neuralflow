import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralflow.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[str] = mapped_column(Text, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[str | None] = mapped_column(Text)  # JSON array
    canvas_data: Mapped[str] = mapped_column(Text, nullable=False, default='{"nodes":[],"edges":[]}')
    execution_mode: Mapped[str] = mapped_column(Text, nullable=False, default="sequential")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime)
    run_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    workspace: Mapped["Workspace"] = relationship(back_populates="workflows")  # noqa: F821
    runs: Mapped[list["Run"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")  # noqa: F821
    snapshots: Mapped[list["WorkflowSnapshot"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")  # noqa: F821


class WorkflowSnapshot(Base):
    __tablename__ = "workflow_snapshots"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(Text, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    snapshot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    canvas_data: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    workflow: Mapped["Workflow"] = relationship(back_populates="snapshots")
