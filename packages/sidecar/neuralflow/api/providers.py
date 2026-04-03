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
    "openrouter": ["openrouter/openai/gpt-4o", "openrouter/anthropic/claude-haiku-3-5", "openrouter/meta-llama/llama-3.3-70b-instruct", "openrouter/qwen/qwen3-235b-a22b:free"],
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
    """Test connectivity for every model listed in default_model (comma-separated).

    Makes a minimal 1-token LiteLLM completion per model to verify the key works.
    Returns per-model results so the UI can show which models are accessible.
    """
    import os
    import time
    import litellm

    p = await db.get(Provider, provider_id)
    if not p:
        raise HTTPException(404, "Provider not found")

    # Ollama: just ping the local API
    if p.provider_type == "ollama":
        try:
            import httpx
            base = (p.base_url or "http://localhost:11434").rstrip("/")
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(f"{base}/api/tags")
                r.raise_for_status()
            return {"ok": True, "models": []}
        except Exception as e:
            return {"ok": False, "error": str(e), "models": []}

    api_key = (
        os.environ.get(f"NEURALFLOW_KEY_{p.provider_type.upper()}")
        or p.api_key_ref
        or None
    )
    if not api_key:
        return {"ok": False, "error": "No API key configured", "models": []}

    # Parse comma-separated model list
    model_names = [m.strip() for m in (p.default_model or "").split(",") if m.strip()]
    if not model_names:
        # Nothing to test — just confirm key is present
        return {"ok": True, "models": [], "note": "No models configured; key is present"}

    results = []
    any_ok = False

    _DIRECT_PROVIDERS = {"openrouter", "lm_studio", "custom"}
    use_direct = p.provider_type in _DIRECT_PROVIDERS or bool(p.base_url)

    for model in model_names:
        t0 = int(time.time() * 1000)
        try:
            if use_direct:
                import httpx as _httpx
                if p.provider_type == "openrouter":
                    base_url = (p.base_url or "https://openrouter.ai/api/v1").rstrip("/")
                    # Strip "openrouter/" routing prefix for the actual API call
                    api_model = model[len("openrouter/"):] if model.startswith("openrouter/") else model
                else:
                    base_url = (p.base_url or "").rstrip("/")
                    api_model = model

                headers = {"Content-Type": "application/json"}
                if api_key:
                    headers["Authorization"] = f"Bearer {api_key}"
                if "openrouter.ai" in base_url:
                    headers["HTTP-Referer"] = "https://neuralflow.app"
                    headers["X-Title"] = "NeuralFlow"

                async with _httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json={"model": api_model, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 1},
                    )
                if resp.status_code not in (200, 201):
                    raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            else:
                kwargs: dict = dict(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=1,
                )
                if api_key:
                    kwargs["api_key"] = api_key
                if p.base_url:
                    kwargs["api_base"] = p.base_url
                await litellm.acompletion(**kwargs)

            latency = int(time.time() * 1000) - t0
            results.append({"model": model, "ok": True, "latency_ms": latency})
            any_ok = True
        except Exception as exc:
            results.append({"model": model, "ok": False, "error": str(exc)})

    return {"ok": any_ok, "models": results}
