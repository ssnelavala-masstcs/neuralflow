"""Prompt optimizer — analyzes and suggests improvements to agent system prompts."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("neuralflow.prompt_optimizer")


@dataclass
class PromptAnalysis:
    score: int  # 0-100
    issues: list[str]
    suggestions: list[str]
    optimized_prompt: str | None = None


def analyze_prompt(system_prompt: str) -> PromptAnalysis:
    """Analyze a system prompt and return issues and suggestions."""
    issues = []
    suggestions = []
    score = 100

    if not system_prompt.strip():
        issues.append("System prompt is empty.")
        suggestions.append("Add a clear role definition and task description.")
        score -= 50
        return PromptAnalysis(score=max(0, score), issues=issues, suggestions=suggestions)

    lines = system_prompt.strip().split("\n")

    # Check for role definition
    if not any(kw in system_prompt.lower() for kw in ["you are", "you're a", "your role", "act as", "role:"]):
        issues.append("No clear role definition found.")
        suggestions.append("Start with 'You are a...' to define the agent's role clearly.")
        score -= 15

    # Check for output format
    if not any(kw in system_prompt.lower() for kw in ["output format", "respond with", "return", "format:", "structure:"]):
        issues.append("No output format specified.")
        suggestions.append("Add an output format section to ensure consistent responses.")
        score -= 10

    # Check for constraints
    if not any(kw in system_prompt.lower() for kw in ["do not", "never", "avoid", "constraint", "limit", "must not"]):
        issues.append("No constraints defined.")
        suggestions.append("Add constraints to prevent unwanted behaviors.")
        score -= 10

    # Check for examples
    if not any(kw in system_prompt.lower() for kw in ["example", "for instance", "e.g.", "such as"]):
        issues.append("No examples provided.")
        suggestions.append("Add examples to illustrate expected behavior.")
        score -= 10

    # Check length
    word_count = len(system_prompt.split())
    if word_count < 20:
        issues.append(f"Prompt is very short ({word_count} words).")
        suggestions.append("Expand the prompt with more detail about the task.")
        score -= 15
    elif word_count > 2000:
        issues.append(f"Prompt is very long ({word_count} words).")
        suggestions.append("Consider simplifying or splitting into sections.")
        score -= 5

    # Check for contradictions
    lower = system_prompt.lower()
    if ("always" in lower and "never" in lower and
        any(lower.count(kw) > 2 for kw in ["always", "never", "must"])):
        issues.append("Possible contradictory instructions.")
        suggestions.append("Review instructions for consistency.")
        score -= 10

    # Generate optimized version
    optimized = None
    if issues:
        optimized = _generate_optimized_prompt(system_prompt, suggestions)

    return PromptAnalysis(
        score=max(0, score),
        issues=issues,
        suggestions=suggestions,
        optimized_prompt=optimized,
    )


def _generate_optimized_prompt(original: str, suggestions: list[str]) -> str:
    """Generate an optimized version of the prompt."""
    parts = [original.strip()]
    parts.append("\n\n--- Guidelines ---")
    parts.append("1. Follow the instructions precisely.")
    parts.append("2. If uncertain, state your uncertainty clearly.")
    parts.append("3. Provide structured, well-organized responses.")
    return "\n".join(parts)
