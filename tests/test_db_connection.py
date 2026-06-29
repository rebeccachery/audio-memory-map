import pytest

from backend.db.connection import get_db_connection


def test_get_db_connection_requires_postgres_url(monkeypatch):
    monkeypatch.delenv("POSTGRES_URL", raising=False)

    with pytest.raises(RuntimeError, match="POSTGRES_URL is not set"):
        get_db_connection()
