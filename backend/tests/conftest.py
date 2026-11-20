"""Configuración común de pytest.

Antes de importar la app se sustituye ``DATABASE_URL`` por ``TEST_DATABASE_URL``
y se aborta toda la sesión si esa URL apunta a Supabase.
"""

import os
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.db_guard import UnsafeTestDatabaseError, assert_local_test_database

try:
    _TEST_DATABASE_URL = assert_local_test_database(os.environ.get("TEST_DATABASE_URL"))
except UnsafeTestDatabaseError as exc:
    pytest.exit(str(exc), returncode=2)

os.environ["DATABASE_URL"] = _TEST_DATABASE_URL
os.environ["APP_ENV"] = "test"
os.environ["DEBUG"] = "false"


def _clear_caches() -> None:
    from app.core import config, db

    config.get_settings.cache_clear()
    db._session_factory.cache_clear()
    if db.get_engine.cache_info().currsize:
        db.get_engine().dispose()
    db.get_engine.cache_clear()


@pytest.fixture
def app() -> Iterator[FastAPI]:
    _clear_caches()
    from app.main import create_app

    application = create_app()
    yield application
    application.dependency_overrides.clear()
    _clear_caches()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
