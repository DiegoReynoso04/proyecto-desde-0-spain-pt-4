from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Settings

LOCAL_URL = "postgresql+psycopg://tallerya:pw@db:5432/tallerya_test"
SUPABASE_URL = (
    "postgresql+psycopg://postgres.ref:pw@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
)


def _valid_values(**overrides: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "database_url": LOCAL_URL,
        "jwt_secret_key": "a" * 32,
        "jwt_refresh_secret_key": "b" * 32,
        "password_reset_secret_key": "c" * 32,
        "csrf_secret_key": "d" * 32,
        "payment_simulation_secret": "e" * 32,
    }
    values.update(overrides)
    return values


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita que las variables reales del entorno interfieran."""
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)


def test_valid_settings_load() -> None:
    settings = Settings(**_valid_values())
    assert settings.db_schema == "tallerya"
    assert settings.course_max_capacity == 10
    assert settings.database_provider == "postgresql"


def test_cors_origins_from_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000, https://tallerya.es")
    settings = Settings(**_valid_values())
    assert settings.cors_origins == ["http://localhost:3000", "https://tallerya.es"]


def test_missing_required_variable_fails() -> None:
    values = _valid_values()
    del values["jwt_secret_key"]
    with pytest.raises(ValidationError, match="jwt_secret_key"):
        Settings(**values)


def test_short_secret_fails() -> None:
    with pytest.raises(ValidationError, match="al menos 32 caracteres"):
        Settings(**_valid_values(csrf_secret_key="x" * 31))


def test_placeholder_secret_fails() -> None:
    with pytest.raises(ValidationError, match="valor de ejemplo"):
        Settings(**_valid_values(jwt_secret_key="change-me"))


def test_reused_secrets_fail() -> None:
    with pytest.raises(ValidationError, match="distintos"):
        Settings(**_valid_values(jwt_refresh_secret_key="a" * 32))


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://u:p@host/db",
        "postgresql+psycopg://postgres.ref:[PASSWORD]@aws-<n>-<region>.pooler.supabase.com/db",
    ],
)
def test_invalid_database_url_fails(url: str) -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        Settings(**_valid_values(database_url=url))


def test_capacity_above_ten_fails() -> None:
    with pytest.raises(ValidationError, match="course_max_capacity"):
        Settings(**_valid_values(course_max_capacity=11))


@pytest.mark.parametrize("schema", ["public", "Tallerya", "tallerya;drop"])
def test_invalid_schema_fails(schema: str) -> None:
    with pytest.raises(ValidationError, match="DB_SCHEMA"):
        Settings(**_valid_values(db_schema=schema))


def test_production_requires_secure_cookies_and_no_debug() -> None:
    with pytest.raises(ValidationError, match="COOKIE_SECURE"):
        Settings(**_valid_values(app_env="production", cookie_secure=False))
    with pytest.raises(ValidationError, match="DEBUG"):
        Settings(**_valid_values(app_env="production", cookie_secure=True, debug=True))
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(**_valid_values(app_env="production", cookie_secure=True, cors_origins=["*"]))


def test_supabase_provider_label() -> None:
    assert Settings(**_valid_values(database_url=SUPABASE_URL)).database_provider == "supabase"


def test_secrets_are_not_exposed_in_repr() -> None:
    settings = Settings(**_valid_values())
    rendered = repr(settings) + str(settings.model_dump())
    assert "a" * 32 not in rendered
    assert "tallerya:pw" not in rendered
