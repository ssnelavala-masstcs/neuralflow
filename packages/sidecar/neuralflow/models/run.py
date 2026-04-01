import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neuralflow.database import Base


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(Text, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    workflow_snapshot: Mapped[str] = mapped_column(Text, nullable=False)  # JSON copy of canvas_data at run time
    status: Mapped[str] = mapped_column(Text, nullable=False, default="queued")
    trigger_type: Mapped[str] = mapped_column(Text, nullable=False, default="manual")
    input_data: Mapped[str | None] = mapped_column(Text)   # JSON
    output_data: Mapped[str | None] = mapped_column(Text)  # JSON
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    total_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    metadata_: Mapped[str | None] = mapped_column("metadata", Text)  # JSON

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")  # noqa: F821
    node_runs: Mapped[list["NodeRun"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class NodeRun(Base):
    __tablename__ = "node_runs"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(Text, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    node_id: Mapped[str] = mapped_column(Text, nullable=False)
    node_type: Mapped[str] = mapped_column(Text, nullable=False)
    node_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    input_data: Mapped[str | None] = mapped_column(Text)   # JSON
    output_data: Mapped[str | None] = mapped_column(Text)  # JSON
    error_message: Mapped[str | None] = mapped_column(Text)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    run: Mapped["Run"] = relationship(back_populates="node_runs")
    llm_calls: Mapped[list["LlmCall"]] = relationship(back_populates="node_run", cascade="all, delete-orphan")
    tool_calls: Mapped[list["ToolCallRecord"]] = relationship(back_populates="node_run", cascade="all, delete-orphan")


class LlmCall(Base):
    __tablename__ = "llm_calls"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    node_run_id: Mapped[str] = mapped_column(Text, ForeignKey("node_runs.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[str] = mapped_column(Text, nullable=False)  # denormalized
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    call_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    messages: Mapped[str] = mapped_column(Text, nullable=False)   # JSON
    response: Mapped[str] = mapped_column(Text, nullable=False)   # JSON
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cache_read_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cache_write_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    finish_reason: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    node_run: Mapped["NodeRun"] = relationship(back_populates="llm_calls")
    tool_calls: Mapped[list["ToolCallRecord"]] = relationship(back_populates="llm_call", cascade="all, delete-orphan")


class ToolCallRecord(Base):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    llm_call_id: Mapped[str | None] = mapped_column(Text, ForeignKey("llm_calls.id", ondelete="CASCADE"))
    node_run_id: Mapped[str] = mapped_column(Text, ForeignKey("node_runs.id", ondelete="CASCADE"), nullable=False)
    run_id: Mapped[str] = mapped_column(Text, nullable=False)  # denormalized
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    tool_source: Mapped[str] = mapped_column(Text, nullable=False)  # builtin | mcp:<server> | custom
    input_data: Mapped[str] = mapped_column(Text, nullable=False)   # JSON
    output_data: Mapped[str | None] = mapped_column(Text)           # JSON
    error: Mapped[str | None] = mapped_column(Text)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    node_run: Mapped["NodeRun"] = relationship(back_populates="tool_calls")
    llm_call: Mapped["LlmCall | None"] = relationship(back_populates="tool_calls")
