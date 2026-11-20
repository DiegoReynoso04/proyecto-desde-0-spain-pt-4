import pytest

from tests.db_guard import UnsafeTestDatabaseError, assert_local_test_database


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://postgres.ref:pw@aws-0-eu-west-1.pooler.supabase.com:5432/postgres",
        "postgresql+psycopg://postgres:pw@db.ref.SUPABASE.CO:5432/postgres",
    ],
)
def test_rejects_supabase_urls(url: str) -> None:
    with pytest.raises(UnsafeTestDatabaseError, match="Supabase"):
        assert_local_test_database(url)


@pytest.mark.parametrize("url", [None, ""])
def test_rejects_missing_url(url: str | None) -> None:
    with pytest.raises(UnsafeTestDatabaseError, match="no está definida"):
        assert_local_test_database(url)


def test_rejects_other_drivers() -> None:
    with pytest.raises(UnsafeTestDatabaseError, match="psycopg"):
        assert_local_test_database("sqlite:///test.db")


def test_accepts_local_postgres() -> None:
    url = "postgresql+psycopg://tallerya:pw@db:5432/tallerya_test"
    assert assert_local_test_database(url) == url
