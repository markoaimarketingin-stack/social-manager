from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session


async def db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


DbSession = Depends(db_session_dependency)
