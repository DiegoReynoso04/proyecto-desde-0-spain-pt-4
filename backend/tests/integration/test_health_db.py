"""Health contra el PostgreSQL local de tests (nunca Supabase)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import get_settings
from app.core.db import get_engine

pytestmark = pytest.mark.integration


def test_health_ok_against_local_database(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] == "test"
    assert body["database"]["status"] == "ok"
    assert body["database"]["provider"] == "postgresql"
    assert body["database"]["latency_ms"] >= 0


def test_connections_use_project_schema(client: TestClient) -> None:
    with get_engine().connect() as connection:
        search_path = connection.execute(text("SHOW search_path")).scalar_one()
        # Tras un rollback el search_path debe mantenerse.
        connection.rollback()
        after_rollback = connection.execute(text("SHOW search_path")).scalar_one()
    assert search_path == get_settings().db_schema
    assert after_rollback == search_path
