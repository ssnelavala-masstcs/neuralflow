import os
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from neuralflow.config import settings


class Base(DeclarativeBase):
    pass


def _db_path() -> Path:
    p = Path(settings.default_workspace_dir).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    return p / "data.db"


def make_engine(db_path: Path | None = None):
    path = db_path or _db_path()
    url = f"sqlite+aiosqlite:///{path}"
    return create_async_engine(url, echo=False, future=True)


engine = make_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create all tables on first startup (before Alembic takes over)."""
    # Import all models so Base.metadata is populated
    from neuralflow.models import workspace, workflow, run, provider, mcp_server, memory, schedule, evaluation  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
