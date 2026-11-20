"""Motor de SQLAlchemy y sesiones.

El código solo depende de ``DATABASE_URL``. En desarrollo/producción apunta al
Session pooler de Supabase; en tests, al PostgreSQL local del contenedor ``db``.
"""

from collections.abc import Iterator
from functools import lru_cache
from typing import Any

from psycopg import sql
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


def build_engine(settings: Settings) -> Engine:
    engine = create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        echo=settings.db_echo,
        connect_args={"connect_timeout": settings.db_connect_timeout_seconds},
    )
    _install_search_path(engine, settings.db_schema)
    return engine


def _install_search_path(engine: Engine, schema: str) -> None:
    """Fija ``search_path`` al esquema propio en cada conexión nueva.

    Se hace en autocommit para que el ``SET`` no se pierda con un rollback.
    """

    statement = sql.SQL("SET search_path TO {}").format(sql.Identifier(schema))

    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_connection: Any, _record: Any) -> None:
        previous = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        with dbapi_connection.cursor() as cursor:
            cursor.execute(statement)
        dbapi_connection.autocommit = previous


@lru_cache
def get_engine() -> Engine:
    return build_engine(get_settings())


@lru_cache
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión por petición."""
    with _session_factory()() as session:
        yield session
