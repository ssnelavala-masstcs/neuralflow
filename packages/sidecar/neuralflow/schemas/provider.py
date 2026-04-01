from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ProviderCreate(BaseModel):
    name: str
    provider_type: str
    base_url: str | None = None
    api_key_ref: str | None = None
    default_model: str | None = None
    extra_config: dict[str, Any] | None = None


class ProviderUpdate(BaseModel):
    name: str | None = None
    base_url: str | None = None
    api_key_ref: str | None = None
    default_model: str | None = None
    extra_config: dict[str, Any] | None = None
    is_active: bool | None = None


class ProviderOut(BaseModel):
    id: str
    name: str
    provider_type: str
    base_url: str | None
    api_key_ref: str | None
    default_model: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModelInfo(BaseModel):
    id: str
    name: str
    context_window: int | None = None
    input_cost_per_1m: float | None = None
    output_cost_per_1m: float | None = None
