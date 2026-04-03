"""Tests for prompt optimizer service."""
import pytest
from neuralflow.services.prompt_optimizer import analyze_prompt


def test_empty_prompt():
    result = analyze_prompt("")
    assert result.score <= 50
    assert len(result.issues) > 0
    assert len(result.suggestions) > 0


def test_good_prompt():
    prompt = """You are a research assistant. Your role is to:
1. Search the web for relevant information
2. Summarize findings concisely
3. Cite sources

Output format: Provide a structured summary with bullet points.

Do not make up information. If you don't know, say so.

Example:
User: What is quantum computing?
Assistant: Quantum computing uses quantum mechanics..."""

    result = analyze_prompt(prompt)
    assert result.score >= 70
    assert len(result.issues) == 0


def test_short_prompt():
    result = analyze_prompt("Help the user.")
    assert result.score < 70
    assert len(result.issues) > 0


def test_no_role_definition():
    result = analyze_prompt("Answer questions about code.")
    assert any("role" in issue.lower() for issue in result.issues)


def test_no_output_format():
    result = analyze_prompt("You are a coding assistant. Help users with their questions.")
    assert any("output format" in s.lower() for s in result.suggestions)
