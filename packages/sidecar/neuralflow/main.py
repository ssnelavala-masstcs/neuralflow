from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neuralflow.config import settings
from neuralflow.database import init_db
from neuralflow.logging_config import setup_logging, logger

# Configure structured logging before anything else
setup_logging(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("sidecar_startup", extra={"host": settings.host, "port": settings.port})
    await init_db()
    from neuralflow.scheduling.scheduler import reload_all_triggers, start_scheduler
    start_scheduler()
    await reload_all_triggers()
    yield
    from neuralflow.scheduling.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("sidecar_shutdown")


def _register_routers(app: FastAPI) -> None:
    """Attach all API routers to the app."""
    from neuralflow.api.health import router as health_router
    from neuralflow.api.workflows import router as workflows_router
    from neuralflow.api.providers import router as providers_router
    from neuralflow.api.runs import router as runs_router
    from neuralflow.api.tools import router as tools_router
    from neuralflow.api.mcp import router as mcp_router
    from neuralflow.api.templates import router as templates_router
    from neuralflow.api.analytics import router as analytics_router
    from neuralflow.api.memory import router as memory_router
    from neuralflow.api.scheduling import router as scheduling_router
    from neuralflow.api.export import router as export_router
    from neuralflow.api.snapshots import router as snapshots_router
    from neuralflow.api.evaluation import router as evaluation_router
    from neuralflow.api.auth import router as auth_router
    from neuralflow.api.plugins import router as plugins_router
    from neuralflow.api.sharing import router as sharing_router
    from neuralflow.api.notifications import router as notifications_router
    from neuralflow.api.audit import router as audit_router
    from neuralflow.api.agent_memory import router as agent_memory_router
    from neuralflow.api.quota import router as quota_router
    from neuralflow.api.prompt_optimizer import router as prompt_optimizer_router
    from neuralflow.api.auto_debug import router as auto_debug_router
    from neuralflow.api.mcp_registry import router as mcp_registry_router
    from neuralflow.api.ai_builder import router as ai_builder_router
    from neuralflow.api.swarm import router as swarm_router
    from neuralflow.api.subagent import router as subagent_router

    app.include_router(health_router)
    app.include_router(workflows_router)
    app.include_router(providers_router)
    app.include_router(runs_router)
    app.include_router(tools_router)
    app.include_router(mcp_router)
    app.include_router(templates_router)
    app.include_router(analytics_router)
    app.include_router(memory_router)
    app.include_router(scheduling_router)
    app.include_router(export_router)
    app.include_router(snapshots_router)
    app.include_router(evaluation_router)
    app.include_router(auth_router)
    app.include_router(plugins_router)
    app.include_router(sharing_router)
    app.include_router(notifications_router)
    app.include_router(audit_router)
    app.include_router(agent_memory_router)
    app.include_router(quota_router)
    app.include_router(prompt_optimizer_router)
    app.include_router(auto_debug_router)
    app.include_router(mcp_registry_router)
    app.include_router(ai_builder_router)
    app.include_router(swarm_router)
    app.include_router(subagent_router)


def _add_middleware(app: FastAPI) -> None:
    """Attach all middleware to the app."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    from neuralflow.middleware.rate_limit import RateLimitMiddleware
    app.add_middleware(
        RateLimitMiddleware,
        default_limit=100,
        window_seconds=60,
        overrides={"/api/runs": 10},
    )

    from neuralflow.middleware.request_size import RequestSizeMiddleware
    app.add_middleware(RequestSizeMiddleware)

    from neuralflow.middleware.audit_log import AuditMiddleware
    app.add_middleware(AuditMiddleware)

    from neuralflow.middleware.error_handler import register_error_handler
    register_error_handler(app)


def create_app(testing: bool = False) -> FastAPI:
    """Factory function to create the FastAPI application.

    Args:
        testing: If True, skip lifespan (no DB init, no scheduler) and skip
            middleware (rate limiter, request size) so tests can use the
            ASGI test client without Starlette middleware compatibility issues.
    """
    app_lifespan = None if testing else lifespan

    application = FastAPI(
        title="NeuralFlow Sidecar",
        version="0.1.0",
        lifespan=app_lifespan,
        docs_url="/docs",
        redoc_url=None,
    )

    # CORS is always needed for the Tauri webview
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
    )

    if not testing:
        from neuralflow.middleware.rate_limit import RateLimitMiddleware
        application.add_middleware(
            RateLimitMiddleware,
            default_limit=100,
            window_seconds=60,
            overrides={"/api/runs": 10},
        )

        from neuralflow.middleware.request_size import RequestSizeMiddleware
        application.add_middleware(RequestSizeMiddleware)

        from neuralflow.middleware.audit_log import AuditMiddleware
        application.add_middleware(AuditMiddleware)

    from neuralflow.middleware.error_handler import register_error_handler
    register_error_handler(application)

    _register_routers(application)
    return application


# Default app instance for production (uvicorn neuralflow.main:app)
app = create_app()
logger.info("sidecar_ready")
