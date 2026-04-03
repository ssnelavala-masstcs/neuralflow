"""Auto-debug service — AI diagnoses workflow failures and suggests fixes."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("neuralflow.auto_debug")


@dataclass
class DebugReport:
    root_cause: str
    suggested_fix: str
    confidence: float  # 0.0 - 1.0
    details: dict[str, Any] = field(default_factory=dict)
    alternative_fixes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_cause": self.root_cause,
            "suggested_fix": self.suggested_fix,
            "confidence": round(self.confidence, 2),
            "details": self.details,
            "alternative_fixes": self.alternative_fixes,
        }


def diagnose_failure(
    error_message: str,
    node_type: str | None = None,
    node_config: dict[str, Any] | None = None,
    llm_calls: list[dict[str, Any]] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> DebugReport:
    """Diagnose a workflow failure and suggest fixes."""
    error_lower = error_message.lower()

    # Pattern matching for common failures
    if any(kw in error_lower for kw in ["api key", "authentication", "unauthorized", "401"]):
        return DebugReport(
            root_cause="API authentication failed. The API key may be invalid or expired.",
            suggested_fix="Update the API key in Provider Settings.",
            confidence=0.9,
            details={"error": error_message},
            alternative_fixes=[
                "Check if the provider is experiencing an outage.",
                "Verify the API key has the required permissions.",
            ],
        )

    if any(kw in error_lower for kw in ["rate limit", "429", "too many requests"]):
        return DebugReport(
            root_cause="Rate limit exceeded on the LLM provider.",
            suggested_fix="Wait a few minutes and retry. Consider reducing request frequency.",
            confidence=0.95,
            details={"error": error_message},
            alternative_fixes=[
                "Switch to a provider with higher rate limits.",
                "Add delays between agent calls.",
            ],
        )

    if any(kw in error_lower for kw in ["context length", "token limit", "maximum context"]):
        return DebugReport(
            root_cause="Context window exceeded. The conversation is too long for the model.",
            suggested_fix="Reduce max_tokens or use a model with a larger context window.",
            confidence=0.85,
            details={"error": error_message},
            alternative_fixes=[
                "Enable auto-compact to summarize long conversations.",
                "Shorten the system prompt.",
            ],
        )

    if any(kw in error_lower for kw in ["timeout", "timed out", "connection refused"]):
        return DebugReport(
            root_cause="Connection to the LLM provider timed out or was refused.",
            suggested_fix="Check your network connection and the provider's status.",
            confidence=0.8,
            details={"error": error_message},
            alternative_fixes=[
                "If using a custom base URL, verify it's accessible.",
                "Try a different provider.",
            ],
        )

    if any(kw in error_lower for kw in ["tool", "not found", "unknown tool"]):
        return DebugReport(
            root_cause="A tool call referenced a tool that doesn't exist.",
            suggested_fix="Check the tool configuration and ensure the tool is registered.",
            confidence=0.85,
            details={"error": error_message},
            alternative_fixes=[
                "Install the required MCP server.",
                "Verify the tool name matches exactly.",
            ],
        )

    if any(kw in error_lower for kw in ["json", "parse", "decode", "invalid"]):
        return DebugReport(
            root_cause="Failed to parse JSON response from the LLM.",
            suggested_fix="The LLM returned malformed JSON. Retry or use a more capable model.",
            confidence=0.7,
            details={"error": error_message},
            alternative_fixes=[
                "Add stricter JSON output instructions to the system prompt.",
                "Use a model with better JSON formatting.",
            ],
        )

    # Generic fallback
    return DebugReport(
        root_cause=f"Workflow failed with: {error_message}",
        suggested_fix="Review the run log for details. Check node configurations and try again.",
        confidence=0.4,
        details={"error": error_message, "node_type": node_type},
        alternative_fixes=[
            "Simplify the workflow and test each node individually.",
            "Check the sidecar logs for additional error details.",
        ],
    )
