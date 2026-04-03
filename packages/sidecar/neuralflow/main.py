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


app = FastAPI(
    title="NeuralFlow Sidecar",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

# ── CORS — explicit methods and headers ──────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
from neuralflow.middleware.rate_limit import build_rate_limit_middleware

app.add_middleware(
    build_rate_limit_middleware(
        default_limit=100,
        window_seconds=60,
        overrides={"/api/runs": 10},
    )
)

# ── Request size limiting ─────────────────────────────────────────────────────
from neuralflow.middleware.request_size import build_request_size_middleware

app.add_middleware(build_request_size_middleware())

# ── Global error handler ──────────────────────────────────────────────────────
from neuralflow.middleware.error_handler import register_error_handler

register_error_handler(app)

# ── Register routers ──────────────────────────────────────────────────────────
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

logger.info("sidecar_ready")
