from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def _to_async_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return database_url


def get_engine() -> AsyncEngine:
    global engine, SessionLocal

    if engine is None:
        engine = create_async_engine(_to_async_database_url(settings.database_url), future=True)
        SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global SessionLocal

    if SessionLocal is None:
        get_engine()

    assert SessionLocal is not None
    return SessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session


async def ping_database() -> bool:
    try:
        session_factory = get_session_factory()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def close_engine() -> None:
    global engine, SessionLocal

    if engine is not None:
        await engine.dispose()
    engine = None
    SessionLocal = None
