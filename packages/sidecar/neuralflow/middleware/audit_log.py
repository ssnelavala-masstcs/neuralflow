"""Audit log middleware — records every API request for compliance and debugging."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("neuralflow.audit")


@dataclass
class AuditEntry:
    id: str
    timestamp: float
    method: str
    path: str
    status_code: int
    duration_ms: float
    user_agent: str | None = None
    remote_addr: str | None = None
    request_size: int | None = None
    response_size: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "method": self.method,
            "path": self.path,
            "status_code": self.status_code,
            "duration_ms": round(self.duration_ms, 2),
            "user_agent": self.user_agent,
            "remote_addr": self.remote_addr,
            "request_size": self.request_size,
            "response_size": self.response_size,
        }


class AuditLog:
    """In-memory audit log with configurable retention."""

    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: list[AuditEntry] = []
        self._max_entries = max_entries

    def add(self, entry: AuditEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

    def query(
        self,
        start_time: float | None = None,
        end_time: float | None = None,
        method: str | None = None,
        path_prefix: str | None = None,
        status_min: int | None = None,
        status_max: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        results = self._entries
        if start_time is not None:
            results = [e for e in results if e.timestamp >= start_time]
        if end_time is not None:
            results = [e for e in results if e.timestamp <= end_time]
        if method is not None:
            results = [e for e in results if e.method == method]
        if path_prefix is not None:
            results = [e for e in results if e.path.startswith(path_prefix)]
        if status_min is not None:
            results = [e for e in results if e.status_code >= status_min]
        if status_max is not None:
            results = [e for e in results if e.status_code <= status_max]
        return [e.to_dict() for e in reversed(results[:limit])]

    def clear(self) -> None:
        self._entries.clear()

    @property
    def total_entries(self) -> int:
        return len(self._entries)


# Global singleton
audit_log = AuditLog()


class AuditMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that logs every request to the audit trail."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000

        content_length = response.headers.get("content-length")
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_agent=request.headers.get("user-agent"),
            remote_addr=request.client.host if request.client else None,
            request_size=int(request.headers.get("content-length", 0)),
            response_size=int(content_length) if content_length else None,
        )
        audit_log.add(entry)
        return response
