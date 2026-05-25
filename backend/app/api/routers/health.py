from fastapi import APIRouter

from app.schemas.health import HealthResponse, StatusResponse
from app.services.health_service import get_health_status, get_system_status

router = APIRouter(tags=["health"])
versioned_router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return get_health_status()


@versioned_router.get("/health", response_model=HealthResponse)
async def versioned_health_check() -> HealthResponse:
    return get_health_status()


@versioned_router.get("/system/status", response_model=StatusResponse, tags=["system"])
async def system_status() -> StatusResponse:
    return await get_system_status()
