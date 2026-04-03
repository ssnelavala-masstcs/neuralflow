"""Global exception handler — consistent JSON error responses, no stack traces."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from neuralflow.errors import NeuralFlowError

logger = logging.getLogger("neuralflow.error_handler")


def register_error_handler(app: FastAPI) -> None:
    """Attach exception handlers to *app* so every error returns structured JSON."""

    @app.exception_handler(NeuralFlowError)
    async def neuralflow_error_handler(request: Request, exc: NeuralFlowError):
        logger.warning("NeuralFlowError: %s on %s %s", exc.code, request.method, request.url.path)
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"http_{exc.status_code}",
                    "message": exc.detail,
                    "details": None,
                    "recovery_hint": None,
                    "severity": "warning",
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                    "recovery_hint": None,
                    "severity": "warning",
                }
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                    "recovery_hint": None,
                    "severity": "warning",
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An internal error occurred.",
                    "details": None,
                    "recovery_hint": "Try refreshing or restarting the application.",
                    "severity": "critical",
                }
            },
        )
