import logging
import time

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.health import DatabaseHealth

logger = logging.getLogger(__name__)


def check_database(engine: Engine, provider: str) -> DatabaseHealth:
    """Ejecuta ``SELECT 1`` y mide la latencia.

    Ante un fallo no se expone el mensaje del driver (podría incluir el host o
    el usuario), solo el tipo de excepción.
    """
    started = time.perf_counter()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
    except SQLAlchemyError as exc:
        error = type(exc).__name__
        logger.warning("Health check de BD fallido: %s", error)
        return DatabaseHealth(status="error", provider=provider, error=error)
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    return DatabaseHealth(status="ok", provider=provider, latency_ms=latency_ms)
