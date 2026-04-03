"""In-memory per-IP rate limiting middleware using a sliding window."""

import time
from collections import defaultdict
from typing import Callable

from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimiter:
    """Sliding-window rate limiter keyed by client IP."""

    def __init__(self, default_limit: int = 100, window_seconds: int = 60) -> None:
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        # ip -> list[timestamp]
        self._requests: dict[str, list[float]] = defaultdict(list)
        # path_prefix -> limit override
        self._overrides: dict[str, int] = {}

    def set_limit(self, path_prefix: str, limit: int) -> None:
        """Set a custom rate limit for endpoints matching *path_prefix*."""
        self._overrides[path_prefix] = limit

    def _clean(self, ip: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._requests[ip] = [t for t in self._requests[ip] if t > cutoff]

    def _limit_for_path(self, path: str) -> int:
        for prefix, limit in self._overrides.items():
            if path.startswith(prefix):
                return limit
        return self.default_limit

    def is_allowed(self, ip: str, path: str) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds)."""
        now = time.time()
        self._clean(ip, now)
        limit = self._limit_for_path(path)
        if len(self._requests[ip]) >= limit:
            oldest = self._requests[ip][0]
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, max(retry_after, 1)
        self._requests[ip].append(now)
        return True, 0


# Module-level singleton configured at startup
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def build_rate_limit_middleware(
    default_limit: int = 100,
    window_seconds: int = 60,
    overrides: dict[str, int] | None = None,
) -> Callable:
    """Return an ASGI middleware factory that enforces per-IP rate limits.

    Usage in main.py::

        app.add_middleware(
            build_rate_limit_middleware(
                default_limit=100,
                window_seconds=60,
                overrides={"/api/runs": 10},
            )
        )
    """
    limiter = RateLimiter(default_limit=default_limit, window_seconds=window_seconds)
    if overrides:
        for prefix, limit in overrides.items():
            limiter.set_limit(prefix, limit)

    async def dispatch(request: Request, call_next):
        client_host = request.client.host if request.client else "unknown"
        allowed, retry_after = limiter.is_allowed(client_host, request.url.path)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limited", "message": "Too many requests. Please retry later.", "details": None}},
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)

    return dispatch
