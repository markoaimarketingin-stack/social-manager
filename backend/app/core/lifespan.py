from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import import_models
from app.db.session import close_engine


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    import_models()
    yield
    await close_engine()
