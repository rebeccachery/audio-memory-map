"""Tests for database migration utilities."""

import pytest

from backend.db import migrate as migrate_module


def test_run_migrations_requires_postgres_url(monkeypatch):
    monkeypatch.delenv("POSTGRES_URL", raising=False)

    with pytest.raises(SystemExit) as exc:
        migrate_module.main()

    assert exc.value.code == 1
