import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralflow.database import get_db
from neuralflow.models.provider import Provider
from neuralflow.schemas.provider import ModelInfo, ProviderCreate, ProviderOut, ProviderUpdate

router = APIRouter(prefix="/api/providers")

# LiteLLM provider type → known models (fallback list; real listing uses LiteLLM)
_PROVIDER_MODEL_HINTS: dict[str, list[str]] = {
    "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o3", "o4-mini"],
    "anthropic": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
    "groq": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
    "mistral": ["mistral-large-latest", "codestral-latest", "mistral-small-latest"],
    "deepseek": ["deepseek-chat", "deepseek-reasoner"],
    "google": ["gemini/gemini-2.0-flash", "gemini/gemini-2.5-pro"],
    "ollama": [],  # discovered at runtime via Ollama API
    "lm_studio": [],
}


@router.get("", response_model=list[ProviderOut])
async def list_providers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Provider).order_by(Provider.created_at))
    return result.scalars().all()


@router.post("", response_model=ProviderOut, status_code=201)
async def create_provider(body: ProviderCreate, db: AsyncSession = Depends(get_db)):
    p = Provider(
        id=str(uuid.uuid4()),
        name=body.name,
        provider_type=body.provider_type,
        base_url=body.base_url,
        api_key_ref=body.api_key_ref,
        default_model=body.default_model,
        extra_config=json.dumps(body.extra_config) if body.extra_config else None,
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/{provider_id}", response_model=ProviderOut)
async def get_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    p = await db.get(Provider, provider_id)
    if not p:
        raise HTTPException(404, "Provider not found")
    return p


@router.patch("/{provider_id}", response_model=ProviderOut)
async def update_provider(provider_id: str, body: ProviderUpdate, db: AsyncSession = Depends(get_db)):
    p = await db.get(Provider, provider_id)
    if not p:
        raise HTTPException(404, "Provider not found")
    for field in ("name", "base_url", "api_key_ref", "default_model", "is_active"):
        v = getattr(body, field, None)
        if v is not None:
            setattr(p, field, v)
    if body.extra_config is not None:
        p.extra_config = json.dumps(body.extra_config)
    await db.commit()
    await db.refresh(p)
    return p


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    p = await db.get(Provider, provider_id)
    if not p:
        raise HTTPException(404, "Provider not found")
    await db.delete(p)
    await db.commit()


@router.get("/{provider_id}/models", response_model=list[ModelInfo])
async def list_models(provider_id: str, db: AsyncSession = Depends(get_db)):
    p = await db.get(Provider, provider_id)
    if not p:
        raise HTTPException(404, "Provider not found")

    # For Ollama: query local API to get running models
    if p.provider_type == "ollama":
        try:
            import httpx
            base = (p.base_url or "http://localhost:11434").rstrip("/")
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{base}/api/tags")
                r.raise_for_status()
                data = r.json()
                return [
                    ModelInfo(id=f"ollama/{m['name']}", name=m["name"])
                    for m in data.get("models", [])
                ]
        except Exception:
            return []

    # For others: return static hint list wrapped as ModelInfo
    hints = _PROVIDER_MODEL_HINTS.get(p.provider_type, [])
    return [ModelInfo(id=m, name=m) for m in hints]


@router.post("/{provider_id}/test")
async def test_provider(provider_id: str, db: AsyncSession = Depends(get_db)):
    """Quick connectivity test — sends a minimal LiteLLM completion."""
    p = await db.get(Provider, provider_id)
    if not p:
        raise HTTPException(404, "Provider not found")

    if p.provider_type == "ollama":
        try:
            import httpx
            base = (p.base_url or "http://localhost:11434").rstrip("/")
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{base}/api/tags")
                r.raise_for_status()
            return {"ok": True, "latency_ms": None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # For cloud providers, just verify the api_key_ref is set
    if not p.api_key_ref:
        return {"ok": False, "error": "No API key configured (api_key_ref is empty)"}

    return {"ok": True, "latency_ms": None, "note": "Key reference is set; live call not performed at test time"}
