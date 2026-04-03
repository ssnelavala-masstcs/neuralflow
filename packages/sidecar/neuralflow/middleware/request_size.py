"""Request size limiting middleware."""

from typing import Callable

from starlette.requests import Request
from starlette.responses import JSONResponse

# 10 MB default, 50 MB for file-upload endpoints
_DEFAULT_MAX_BYTES = 10 * 1024 * 1024
_UPLOAD_MAX_BYTES = 50 * 1024 * 1024

_UPLOAD_PATHS = frozenset({
    "/api/export",
    "/api/snapshots",
})


def build_request_size_middleware(
    default_max: int = _DEFAULT_MAX_BYTES,
    upload_max: int = _UPLOAD_MAX_BYTES,
    upload_paths: frozenset[str] | None = None,
) -> Callable:
    """Return an ASGI middleware that rejects oversized request bodies.

    Returns **413 Payload Too Large** when *Content-Length* exceeds the
    configured threshold for the matched path.
    """
    upload = upload_paths if upload_paths is not None else _UPLOAD_PATHS

    async def dispatch(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                size = int(content_length)
            except (ValueError, TypeError):
                size = 0

            limit = upload_max if request.url.path in upload else default_max
            if size > limit:
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "payload_too_large",
                            "message": f"Request body exceeds maximum allowed size of {limit} bytes.",
                            "details": None,
                        }
                    },
                )
        return await call_next(request)

    return dispatch
