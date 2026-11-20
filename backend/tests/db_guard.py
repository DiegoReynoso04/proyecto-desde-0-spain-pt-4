"""Salvaguarda: los tests nunca deben conectarse a Supabase."""

FORBIDDEN_HOST_MARKERS = ("supabase.co", "supabase.com")


class UnsafeTestDatabaseError(RuntimeError):
    pass


def assert_local_test_database(url: str | None) -> str:
    if not url:
        raise UnsafeTestDatabaseError(
            "TEST_DATABASE_URL no está definida: los tests necesitan el PostgreSQL local."
        )
    lowered = url.lower()
    if any(marker in lowered for marker in FORBIDDEN_HOST_MARKERS):
        raise UnsafeTestDatabaseError(
            "TEST_DATABASE_URL apunta a Supabase. Los tests solo pueden usar el PostgreSQL local."
        )
    if not lowered.startswith("postgresql+psycopg://"):
        raise UnsafeTestDatabaseError("TEST_DATABASE_URL debe usar postgresql+psycopg://")
    return url
