"""Request size limiting middleware."""

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

# 10 MB default, 50 MB for file-upload endpoints
_DEFAULT_MAX_BYTES = 10 * 1024 * 1024
_UPLOAD_MAX_BYTES = 50 * 1024 * 1024

_UPLOAD_PATHS = frozenset({
    "/api/export",
    "/api/snapshots",
})


class RequestSizeMiddleware:
    """ASGI middleware that rejects oversized request bodies."""

    def __init__(
        self,
        app: ASGIApp,
        default_max: int = _DEFAULT_MAX_BYTES,
        upload_max: int = _UPLOAD_MAX_BYTES,
        upload_paths: frozenset[str] | None = None,
    ) -> None:
        self.app = app
        self.default_max = default_max
        self.upload_max = upload_max
        self.upload_paths = upload_paths if upload_paths is not None else _UPLOAD_PATHS

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                size = int(content_length)
            except (ValueError, TypeError):
                size = 0

            limit = self.upload_max if request.url.path in self.upload_paths else self.default_max
            if size > limit:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "payload_too_large",
                            "message": f"Request body exceeds maximum allowed size of {limit} bytes.",
                            "details": None,
                        }
                    },
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
