"""Structured error types for NeuralFlow."""

from __future__ import annotations

from typing import Any


class NeuralFlowError(Exception):
    """Base error class with structured fields for user-friendly error responses."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        recovery_hint: str | None = None,
        severity: str = "warning",
        status_code: int = 400,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details
        self.recovery_hint = recovery_hint
        self.severity = severity  # info | warning | critical
        self.status_code = status_code

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "recovery_hint": self.recovery_hint,
                "severity": self.severity,
            }
        }


class WorkflowNotFoundError(NeuralFlowError):
    def __init__(self, workflow_id: str) -> None:
        super().__init__(
            code="workflow_not_found",
            message=f"Workflow '{workflow_id}' not found.",
            recovery_hint="The workflow may have been deleted. Try refreshing the workspace.",
            severity="warning",
            status_code=404,
        )


class WorkspaceNotFoundError(NeuralFlowError):
    def __init__(self, workspace_id: str) -> None:
        super().__init__(
            code="workspace_not_found",
            message=f"Workspace '{workspace_id}' not found.",
            recovery_hint="Check your workspace ID or create a new workspace.",
            severity="warning",
            status_code=404,
        )


class ProviderUnreachableError(NeuralFlowError):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="provider_unreachable",
            message=f"Could not reach the LLM provider '{provider}'.",
            recovery_hint="Check your API key and network connection.",
            severity="warning",
            status_code=502,
        )


class InvalidApiKeyError(NeuralFlowError):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="invalid_api_key",
            message=f"Invalid API key for provider '{provider}'.",
            recovery_hint="Update your provider API key in Settings.",
            severity="warning",
            status_code=401,
        )


class RunFailedError(NeuralFlowError):
    def __init__(self, run_id: str, detail: str | None = None) -> None:
        super().__init__(
            code="run_failed",
            message=f"Workflow run '{run_id}' failed.",
            details={"detail": detail} if detail else None,
            recovery_hint="Check the Run Log for details. You can replay from a specific step.",
            severity="critical",
            status_code=500,
        )


class ValidationError(NeuralFlowError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="validation_failed",
            message=message,
            details=details,
            recovery_hint="Fix the validation errors before running.",
            severity="warning",
            status_code=400,
        )


class RateLimitedError(NeuralFlowError):
    def __init__(self, retry_after: int | None = None) -> None:
        super().__init__(
            code="rate_limited",
            message="Too many requests. Please wait a moment.",
            recovery_hint="You've hit the rate limit. Wait a few seconds and try again.",
            severity="info",
            status_code=429,
            details={"retry_after": retry_after} if retry_after else None,
        )


class PayloadTooLargeError(NeuralFlowError):
    def __init__(self, limit: int) -> None:
        super().__init__(
            code="payload_too_large",
            message=f"Request body exceeds maximum allowed size of {limit} bytes.",
            recovery_hint="Try reducing the size of your input data.",
            severity="info",
            status_code=413,
        )
