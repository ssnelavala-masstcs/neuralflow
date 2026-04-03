from datetime import datetime
from typing import Any

from pydantic import BaseModel


class EvaluationCreate(BaseModel):
    workflow_a_id: str
    workflow_b_id: str
    test_input: dict[str, Any]
    metric: str = "cost"


class EvaluationResultItem(BaseModel):
    run_id: str | None = None
    cost_usd: float = 0.0
    total_tokens: int = 0
    duration_ms: int | None = None
    output: Any = None
    status: str = "unknown"


class EvaluationOut(BaseModel):
    id: str
    workflow_a_id: str
    workflow_b_id: str
    test_input: dict[str, Any]
    metric: str
    status: str
    result_a: EvaluationResultItem | None = None
    result_b: EvaluationResultItem | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, m: Any) -> "EvaluationOut":
        import json
        test_input = json.loads(m.test_input) if isinstance(m.test_input, str) else m.test_input
        result_a = None
        result_b = None
        if m.result_a:
            raw = json.loads(m.result_a) if isinstance(m.result_a, str) else m.result_a
            result_a = EvaluationResultItem(**raw)
        if m.result_b:
            raw = json.loads(m.result_b) if isinstance(m.result_b, str) else m.result_b
            result_b = EvaluationResultItem(**raw)
        return cls(
            id=m.id,
            workflow_a_id=m.workflow_a_id,
            workflow_b_id=m.workflow_b_id,
            test_input=test_input,
            metric=m.metric,
            status=m.status,
            result_a=result_a,
            result_b=result_b,
            error_message=m.error_message,
            created_at=m.created_at,
            completed_at=m.completed_at,
        )
