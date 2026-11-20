"""Tests del endpoint de health que no necesitan base de datos."""

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine

from app.core.db import get_engine

UNREACHABLE_URL = "postgresql+psycopg://nobody:secret-pw@127.0.0.1:1/nowhere"


@pytest.fixture
def broken_engine() -> Iterator[Engine]:
    engine = create_engine(UNREACHABLE_URL, connect_args={"connect_timeout": 1})
    yield engine
    engine.dispose()


def test_liveness_does_not_touch_database(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_reports_degraded_when_database_is_down(
    app: FastAPI, client: TestClient, broken_engine: Engine
) -> None:
    app.dependency_overrides[get_engine] = lambda: broken_engine
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"]["status"] == "error"
    assert body["database"]["error"] == "OperationalError"
    assert body["database"]["latency_ms"] is None
    # No se filtran credenciales ni el host de la conexión.
    assert "secret-pw" not in response.text
    assert "127.0.0.1" not in response.text


def test_security_headers_are_present(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Strict-Transport-Security" not in response.headers  # solo en producción


def test_cors_allows_only_configured_origins(client: TestClient) -> None:
    allowed = client.options(
        "/api/v1/health/live",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert allowed.headers.get("access-control-allow-credentials") == "true"

    denied = client.options(
        "/api/v1/health/live",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" not in denied.headers


def test_openapi_docs_are_served_under_api_prefix(client: TestClient) -> None:
    assert client.get("/api/v1/openapi.json").status_code == 200
    assert client.get("/api/v1/docs").status_code == 200
