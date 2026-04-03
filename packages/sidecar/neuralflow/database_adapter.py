"""Database adapter — supports both SQLite and PostgreSQL."""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Auto-detect database type from environment variable
DATABASE_URL = os.environ.get("NEURALFLOW_DATABASE_URL", "")

if DATABASE_URL.startswith("postgresql://"):
    # Convert postgresql:// to postgresql+asyncpg:// for async support
    ASYNC_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    IS_POSTGRESQL = True
elif DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNC_URL = DATABASE_URL
    IS_POSTGRESQL = True
else:
    # Default to SQLite
    import pathlib
    db_dir = pathlib.Path(os.environ.get("NEURALFLOW_DATA_DIR", str(pathlib.Path.home() / ".neuralflow")))
    db_dir.mkdir(parents=True, exist_ok=True)
    ASYNC_URL = f"sqlite+aiosqlite:///{db_dir / 'data.db'}"
    IS_POSTGRESQL = False

# Connection pool settings for PostgreSQL
POOL_SIZE = int(os.environ.get("NEURALFLOW_DB_POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.environ.get("NEURALFLOW_DB_MAX_OVERFLOW", "10"))

# Create engine
engine_kwargs: dict[str, Any] = {"echo": False}
if IS_POSTGRESQL:
    engine_kwargs["pool_size"] = POOL_SIZE
    engine_kwargs["max_overflow"] = MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(ASYNC_URL, **engine_kwargs)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """FastAPI dependency for getting a database session."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Initialize database tables."""
    from neuralflow.models import Base  # Import all models before creating tables

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


def get_db_type() -> str:
    """Return the database type: 'postgresql' or 'sqlite'."""
    return "postgresql" if IS_POSTGRESQL else "sqlite"
