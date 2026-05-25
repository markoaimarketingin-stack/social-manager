from app.core.config import settings
from app.db.session import ping_database
from app.schemas.health import HealthResponse, StatusResponse


def get_health_status() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
    )


async def get_system_status() -> StatusResponse:
    database_ok = await ping_database()
    return StatusResponse(
        status="ok" if database_ok else "degraded",
        service=settings.app_name,
        environment=settings.app_env,
        database="connected" if database_ok else "unavailable",
    )
