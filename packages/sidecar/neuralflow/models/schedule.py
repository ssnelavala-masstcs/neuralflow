"""ORM model for scheduled workflow triggers."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from neuralflow.database import Base


class ScheduledTrigger(Base):
    __tablename__ = "scheduled_triggers"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_type: Mapped[str] = mapped_column(Text, nullable=False)  # cron | webhook | file_watch
    # cron: APScheduler cron expression fields (combined as "minute hour day month day_of_week")
    cron_expression: Mapped[str | None] = mapped_column(Text)
    # webhook: path under /webhooks/<webhook_path>
    webhook_path: Mapped[str | None] = mapped_column(Text)
    # file_watch: absolute path to watch
    watch_path: Mapped[str | None] = mapped_column(Text)
    # Optional input data injected at trigger time (JSON)
    input_data: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime)
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
