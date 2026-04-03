"""AI Workflow Builder — generates workflow JSON from natural language descriptions."""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger("neuralflow.ai_builder")

# Pattern templates for workflow generation
_PATTERNS: list[dict[str, Any]] = [
    {
        "keywords": ["research", "search", "web", "find", "look up"],
        "name": "Research Workflow",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 50, "y": 200}, "data": {"label": "Trigger", "triggerType": "manual"}},
            {"id": "agent-1", "type": "agent", "position": {"x": 300, "y": 200}, "data": {"label": "Research Agent", "model": "gpt-4o", "system_prompt": "You are a research assistant. Search the web for relevant information and provide a comprehensive summary with citations.", "tools": ["web_search"]}},
            {"id": "output-1", "type": "output", "position": {"x": 550, "y": 200}, "data": {"label": "Research Output"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "agent-1", "type": "data"},
            {"id": "e2", "source": "agent-1", "target": "output-1", "type": "data"},
        ],
    },
    {
        "keywords": ["code", "review", "security", "analyze code", "bug"],
        "name": "Code Review Workflow",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 50, "y": 200}, "data": {"label": "Trigger", "triggerType": "manual"}},
            {"id": "agent-1", "type": "agent", "position": {"x": 250, "y": 100}, "data": {"label": "Security Reviewer", "model": "claude-sonnet-4-20250514", "system_prompt": "You are a security expert. Review the code for vulnerabilities, including SQL injection, XSS, and auth issues.", "tools": ["file_read"]}},
            {"id": "agent-2", "type": "agent", "position": {"x": 250, "y": 300}, "data": {"label": "Quality Reviewer", "model": "gpt-4o", "system_prompt": "You are a senior engineer. Review the code for quality, readability, and best practices.", "tools": ["file_read"]}},
            {"id": "aggregator-1", "type": "aggregator", "position": {"x": 500, "y": 200}, "data": {"label": "Combine Reviews", "strategy": "concat"}},
            {"id": "output-1", "type": "output", "position": {"x": 700, "y": 200}, "data": {"label": "Review Report"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "agent-1", "type": "data"},
            {"id": "e2", "source": "trigger-1", "target": "agent-2", "type": "data"},
            {"id": "e3", "source": "agent-1", "target": "aggregator-1", "type": "data"},
            {"id": "e4", "source": "agent-2", "target": "aggregator-1", "type": "data"},
            {"id": "e5", "source": "aggregator-1", "target": "output-1", "type": "data"},
        ],
    },
    {
        "keywords": ["summarize", "summary", "summarize", "tl;dr", "brief"],
        "name": "Summarization Workflow",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 50, "y": 200}, "data": {"label": "Trigger", "triggerType": "manual"}},
            {"id": "agent-1", "type": "agent", "position": {"x": 300, "y": 200}, "data": {"label": "Summarizer", "model": "gpt-4o-mini", "system_prompt": "You are a summarization expert. Provide a concise summary of the input, highlighting key points.", "max_tokens": 1024}},
            {"id": "output-1", "type": "output", "position": {"x": 550, "y": 200}, "data": {"label": "Summary"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "agent-1", "type": "data"},
            {"id": "e2", "source": "agent-1", "target": "output-1", "type": "data"},
        ],
    },
    {
        "keywords": ["data", "analyze", "analysis", "statistics", "csv", "spreadsheet"],
        "name": "Data Analysis Workflow",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 50, "y": 200}, "data": {"label": "Trigger", "triggerType": "manual"}},
            {"id": "agent-1", "type": "agent", "position": {"x": 300, "y": 200}, "data": {"label": "Data Analyst", "model": "gpt-4o", "system_prompt": "You are a data analyst. Analyze the provided data and return statistical insights, trends, and recommendations.", "tools": ["file_read"]}},
            {"id": "output-1", "type": "output", "position": {"x": 550, "y": 200}, "data": {"label": "Analysis Report"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "agent-1", "type": "data"},
            {"id": "e2", "source": "agent-1", "target": "output-1", "type": "data"},
        ],
    },
    {
        "keywords": ["write", "blog", "content", "article", "post", "seo"],
        "name": "Content Writing Workflow",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 50, "y": 200}, "data": {"label": "Trigger", "triggerType": "manual"}},
            {"id": "agent-1", "type": "agent", "position": {"x": 250, "y": 100}, "data": {"label": "Outline Planner", "model": "gpt-4o", "system_prompt": "You are a content strategist. Create a detailed outline for the given topic.", "max_tokens": 2048}},
            {"id": "agent-2", "type": "agent", "position": {"x": 500, "y": 100}, "data": {"label": "Content Writer", "model": "claude-sonnet-4-20250514", "system_prompt": "You are a professional writer. Write engaging, SEO-optimized content based on the outline.", "max_tokens": 4096}},
            {"id": "output-1", "type": "output", "position": {"x": 750, "y": 100}, "data": {"label": "Blog Post"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "agent-1", "type": "data"},
            {"id": "e2", "source": "agent-1", "target": "agent-2", "type": "data"},
            {"id": "e3", "source": "agent-2", "target": "output-1", "type": "data"},
        ],
    },
]


def generate_workflow(description: str) -> dict[str, Any]:
    """Generate a workflow JSON from a natural language description."""
    desc_lower = description.lower()

    # Find best matching pattern
    best_match = None
    best_score = 0
    for pattern in _PATTERNS:
        score = sum(1 for kw in pattern["keywords"] if kw in desc_lower)
        if score > best_score:
            best_score = score
            best_match = pattern

    if best_match and best_score > 0:
        # Clone the pattern with unique IDs
        workflow = {
            "name": best_match["name"],
            "description": description,
            "nodes": _clone_nodes(best_match["nodes"]),
            "edges": _clone_edges(best_match["edges"]),
        }
        return workflow

    # Default: simple research workflow
    return {
        "name": "Custom Workflow",
        "description": description,
        "nodes": _clone_nodes([
            {"id": "trigger-1", "type": "trigger", "position": {"x": 50, "y": 200}, "data": {"label": "Trigger", "triggerType": "manual"}},
            {"id": "agent-1", "type": "agent", "position": {"x": 300, "y": 200}, "data": {"label": "Agent", "model": "gpt-4o", "system_prompt": f"You are a helpful assistant. Task: {description}"}},
            {"id": "output-1", "type": "output", "position": {"x": 550, "y": 200}, "data": {"label": "Output"}},
        ]),
        "edges": _clone_edges([
            {"id": "e1", "source": "trigger-1", "target": "agent-1", "type": "data"},
            {"id": "e2", "source": "agent-1", "target": "output-1", "type": "data"},
        ]),
    }


def _clone_nodes(nodes: list[dict]) -> list[dict]:
    """Clone nodes with new unique IDs."""
    id_map = {}
    result = []
    for node in nodes:
        new_id = f"{node['type']}-{uuid.uuid4().hex[:8]}"
        id_map[node["id"]] = new_id
        result.append({**node, "id": new_id})
    return result


def _clone_edges(edges: list[dict]) -> list[dict]:
    """Clone edges with new IDs."""
    return [{**edge, "id": f"e-{uuid.uuid4().hex[:8]}"} for edge in edges]
