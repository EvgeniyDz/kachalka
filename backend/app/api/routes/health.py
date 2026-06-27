from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["System condition"])


@router.get("/health", response_model=HealthResponse, summary="Check API")
async def health_check() -> HealthResponse:
    """Return basic API status without querying the database."""

    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
    )
