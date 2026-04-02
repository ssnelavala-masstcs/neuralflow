"""Human-in-the-Loop: pause/resume machinery for HumanNode execution."""
from __future__ import annotations

import asyncio
from typing import Any

# run_id → asyncio.Event that gets set when human input arrives
_resume_events: dict[str, asyncio.Event] = {}
# run_id → the human-supplied input dict
_resume_inputs: dict[str, dict[str, Any]] = {}


def create_resume_gate(run_id: str) -> asyncio.Event:
    event = asyncio.Event()
    _resume_events[run_id] = event
    return event


def resolve_resume_gate(run_id: str, human_input: dict[str, Any]) -> bool:
    """Called from the API when a human submits input. Returns False if no gate exists."""
    event = _resume_events.get(run_id)
    if event is None:
        return False
    _resume_inputs[run_id] = human_input
    event.set()
    return True


def get_resume_input(run_id: str) -> dict[str, Any]:
    return _resume_inputs.pop(run_id, {})


def cleanup_run(run_id: str) -> None:
    _resume_events.pop(run_id, None)
    _resume_inputs.pop(run_id, None)


def is_awaiting_input(run_id: str) -> bool:
    event = _resume_events.get(run_id)
    return event is not None and not event.is_set()
