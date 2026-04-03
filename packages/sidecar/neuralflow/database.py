import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from neuralflow.config import settings


class Base(DeclarativeBase):
    pass


def _get_database_url() -> str:
    """Auto-detect database URL from environment or default to SQLite."""
    env_url = os.environ.get("NEURALFLOW_DATABASE_URL", "")
    if env_url:
        if env_url.startswith("postgresql://"):
            return env_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if env_url.startswith("postgresql+asyncpg://"):
            return env_url
        return env_url
    # Default to SQLite
    p = Path(settings.default_workspace_dir).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return f"sqlite+aiosqlite:///{p / 'data.db'}"


DATABASE_URL = _get_database_url()
IS_POSTGRESQL = DATABASE_URL.startswith("postgresql+")

# Connection pool settings for PostgreSQL
POOL_SIZE = int(os.environ.get("NEURALFLOW_DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.environ.get("NEURALFLOW_DB_MAX_OVERFLOW", "10"))

engine_kwargs: dict = {"echo": False, "future": True}
if IS_POSTGRESQL:
    engine_kwargs["pool_size"] = POOL_SIZE
    engine_kwargs["max_overflow"] = MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Backward-compatible alias for tests
def make_engine(db_path: Path | None = None):
    """Create an engine for a specific database path (used in tests)."""
    path = db_path or _get_database_url().split("///")[-1]
    url = f"sqlite+aiosqlite:///{path}" if not str(path).startswith("postgresql") else str(path)
    return create_async_engine(url, echo=False, future=True)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables on first startup (before Alembic takes over)."""
    # Import all models so Base.metadata is populated
    from neuralflow.models import workspace, workflow, run, provider, mcp_server, memory, schedule, evaluation  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
