from fastapi import APIRouter

from app.api.routers.health import router as health_router, versioned_router as versioned_health_router
from app.api.v1.router import router as v1_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(versioned_health_router, prefix=settings.api_v1_prefix)
api_router.include_router(v1_router, prefix=settings.api_v1_prefix)
