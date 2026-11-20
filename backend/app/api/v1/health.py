from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import Engine

from app import __version__
from app.core.config import Settings, get_settings
from app.core.db import get_engine
from app.schemas.health import HealthResponse, LivenessResponse
from app.services.health import check_database

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={503: {"model": HealthResponse, "description": "La BD no responde"}},
    summary="Estado de la API y de la conexión a la base de datos (SELECT 1)",
)
def health(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    engine: Annotated[Engine, Depends(get_engine)],
) -> HealthResponse:
    database = check_database(engine, settings.database_provider)
    ok = database.status == "ok"
    if not ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(
        status="ok" if ok else "degraded",
        app=settings.app_name,
        version=__version__,
        environment=settings.app_env,
        database=database,
    )


@router.get(
    "/health/live",
    response_model=LivenessResponse,
    summary="Liveness: el proceso responde (no toca la BD)",
)
def liveness() -> LivenessResponse:
    return LivenessResponse()
