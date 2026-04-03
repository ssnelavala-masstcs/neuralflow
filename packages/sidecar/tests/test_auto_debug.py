"""Tests for auto-debug service."""
import pytest
from neuralflow.services.auto_debug import diagnose_failure


def test_api_key_error():
    report = diagnose_failure("401 Unauthorized: Invalid API key")
    assert "authentication" in report.root_cause.lower() or "api key" in report.root_cause.lower()
    assert report.confidence >= 0.8


def test_rate_limit_error():
    report = diagnose_failure("429 Too Many Requests: Rate limit exceeded")
    assert "rate limit" in report.root_cause.lower()
    assert report.confidence >= 0.9


def test_context_length_error():
    report = diagnose_failure("Maximum context length exceeded")
    assert "context" in report.root_cause.lower()
    assert len(report.alternative_fixes) > 0


def test_timeout_error():
    report = diagnose_failure("Connection timed out after 30s")
    assert "timeout" in report.root_cause.lower() or "connection" in report.root_cause.lower()


def test_tool_not_found():
    report = diagnose_failure("Tool 'web_search' not found")
    assert "tool" in report.root_cause.lower()


def test_json_parse_error():
    report = diagnose_failure("Failed to parse JSON response")
    assert "json" in report.root_cause.lower()


def test_generic_error():
    report = diagnose_failure("Something went wrong")
    assert report.root_cause
    assert report.suggested_fix
    assert report.confidence < 0.6  # Generic errors have low confidence
