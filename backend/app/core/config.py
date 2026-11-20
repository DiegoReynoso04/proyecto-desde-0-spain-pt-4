"""Configuración de la aplicación leída del entorno con pydantic-settings.

La app falla al arrancar si falta una variable obligatoria o si un secreto
es débil (menos de 32 caracteres o un valor de ejemplo como ``change-me``).
"""

import re
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

MIN_SECRET_LENGTH = 32
MAX_COURSE_CAPACITY = 10
_PLACEHOLDER_SECRETS = {"change-me", "changeme", "secret", "password"}
_SCHEMA_NAME = re.compile(r"^[a-z_][a-z0-9_]{0,62}$")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore", case_sensitive=False)

    # ---------- General ----------
    app_name: str = "TallerYA"
    app_env: Literal["development", "test", "production"] = "development"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    frontend_url: str = "http://localhost:3000"

    # ---------- Base de datos ----------
    database_url: SecretStr
    db_schema: str = "tallerya"
    db_pool_size: int = Field(default=5, ge=1, le=20)
    db_max_overflow: int = Field(default=5, ge=0, le=20)
    db_echo: bool = False
    db_connect_timeout_seconds: int = Field(default=5, ge=1, le=60)

    # ---------- Seguridad ----------
    jwt_secret_key: SecretStr
    jwt_refresh_secret_key: SecretStr
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_expire_minutes: int = Field(default=15, ge=1, le=60)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    password_reset_token_expire_minutes: int = Field(default=30, ge=5, le=240)
    password_reset_secret_key: SecretStr
    csrf_secret_key: SecretStr
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    login_rate_limit: str = "5/minute"
    contact_rate_limit: str = "3/minute"
    login_lockout_minutes: int = Field(default=15, ge=1)

    # ---------- Reglas de negocio ----------
    reservation_hold_hours: int = Field(default=24, ge=1)
    course_max_capacity: int = Field(default=MAX_COURSE_CAPACITY, ge=1, le=MAX_COURSE_CAPACITY)
    expiration_job_interval_minutes: int = Field(default=5, ge=1)
    reminder_hours_before: int = Field(default=24, ge=1)
    currency: Literal["EUR"] = "EUR"

    # ---------- Pago simulado ----------
    payment_provider: Literal["simulated"] = "simulated"
    payment_simulation_secret: SecretStr

    # ---------- Email ----------
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_user: str | None = None
    smtp_password: SecretStr | None = None
    smtp_use_tls: bool = False
    email_from: str = "TallerYA <no-reply@tallerya.local>"
    owner_notification_email: str = "dueno@example.com"

    @field_validator("database_url")
    @classmethod
    def _check_database_url(cls, value: SecretStr) -> SecretStr:
        url = value.get_secret_value()
        if not url.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL debe usar el driver psycopg 3 (postgresql+psycopg://)")
        if "[PASSWORD]" in url or "<region>" in url:
            raise ValueError("DATABASE_URL contiene marcadores sin rellenar")
        return value

    @field_validator("db_schema")
    @classmethod
    def _check_schema(cls, value: str) -> str:
        if not _SCHEMA_NAME.match(value) or value == "public":
            raise ValueError(
                "DB_SCHEMA debe ser un identificador en minúsculas distinto de 'public'"
            )
        return value

    @field_validator(
        "jwt_secret_key",
        "jwt_refresh_secret_key",
        "password_reset_secret_key",
        "csrf_secret_key",
        "payment_simulation_secret",
    )
    @classmethod
    def _check_secret_strength(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        if secret.strip().lower() in _PLACEHOLDER_SECRETS:
            raise ValueError("el secreto tiene un valor de ejemplo; genera uno nuevo")
        if len(secret) < MIN_SECRET_LENGTH:
            raise ValueError(f"el secreto debe tener al menos {MIN_SECRET_LENGTH} caracteres")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _check_production(self) -> Settings:
        if self.app_env == "production":
            if self.debug:
                raise ValueError("DEBUG debe ser false en producción")
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE debe ser true en producción")
            if "*" in self.cors_origins:
                raise ValueError("CORS_ORIGINS no puede ser '*' en producción")
        secrets = [
            self.jwt_secret_key.get_secret_value(),
            self.jwt_refresh_secret_key.get_secret_value(),
            self.password_reset_secret_key.get_secret_value(),
            self.csrf_secret_key.get_secret_value(),
        ]
        if len(set(secrets)) != len(secrets):
            raise ValueError("los secretos JWT, refresh, reset y CSRF deben ser distintos")
        return self

    @property
    def database_provider(self) -> str:
        """Etiqueta informativa del proveedor (no cambia el comportamiento)."""
        url = self.database_url.get_secret_value()
        return "supabase" if ("supabase.com" in url or "supabase.co" in url) else "postgresql"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # los valores vienen del entorno
