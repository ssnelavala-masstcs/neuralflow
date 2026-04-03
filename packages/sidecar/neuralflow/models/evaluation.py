import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from neuralflow.database import Base


class Evaluation(Base):
    """An A/B test comparing two workflow variants."""

    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_a_id: Mapped[str] = mapped_column(Text, nullable=False)
    workflow_b_id: Mapped[str] = mapped_column(Text, nullable=False)
    test_input: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    metric: Mapped[str] = mapped_column(Text, nullable=False, default="cost")  # cost | tokens | duration | quality
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")  # pending | running | complete | error
    result_a: Mapped[str | None] = mapped_column(Text)  # JSON: {run_id, cost, tokens, duration, output}
    result_b: Mapped[str | None] = mapped_column(Text)  # JSON
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
