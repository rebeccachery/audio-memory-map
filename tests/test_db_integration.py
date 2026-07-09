import os

import pytest

from backend.db import migrate as migrate_module


@pytest.mark.integration
def test_migrations_create_signals_and_regions_tables():
    if os.getenv("RUN_DB_INTEGRATION") != "1":
        pytest.skip("Set RUN_DB_INTEGRATION=1 with Docker Postgres running")

    migrate_module.run_migrations()

    from backend.db.connection import get_db_connection

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name IN ('regions', 'signals', 'schema_migrations')
                ORDER BY table_name;
                """
            )
            tables = [row[0] for row in cursor.fetchall()]
    finally:
        conn.close()

    assert tables == ["regions", "schema_migrations", "signals"]

    exit_code = migrate_module.run_migrations()
    assert exit_code == 0
