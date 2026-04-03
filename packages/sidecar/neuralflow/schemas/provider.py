from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProviderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=255)
    provider_type: str = Field(..., min_length=1, max_length=100)
    base_url: str | None = Field(default=None, max_length=2048)
    api_key_ref: str | None = Field(default=None, max_length=500)
    default_model: str | None = Field(default=None, max_length=255)
    extra_config: dict[str, Any] | None = None


class ProviderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    base_url: str | None = Field(default=None, max_length=2048)
    api_key_ref: str | None = Field(default=None, max_length=500)
    default_model: str | None = Field(default=None, max_length=255)
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
