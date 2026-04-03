"""Prompt optimizer API endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from neuralflow.services.prompt_optimizer import analyze_prompt

router = APIRouter(prefix="/api/prompt")


@router.post("/analyze")
async def analyze_system_prompt(body: dict[str, Any]) -> dict[str, Any]:
    """Analyze a system prompt and return optimization suggestions."""
    prompt = body.get("prompt", "")
    result = analyze_prompt(prompt)
    return {
        "score": result.score,
        "issues": result.issues,
        "suggestions": result.suggestions,
        "optimized_prompt": result.optimized_prompt,
    }
