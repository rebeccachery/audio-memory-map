#!/usr/bin/env python3
"""Apply SQL migrations from backend/db/migrations/ in lexicographic order."""

import sys
from pathlib import Path

from backend.db.connection import get_db_connection


MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def ensure_migrations_table(cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )


def applied_migrations(cursor) -> set[str]:
    cursor.execute("SELECT filename FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}


def apply_migration(cursor, sql_file: Path) -> None:
    cursor.execute(sql_file.read_text(encoding="utf-8"))
    cursor.execute(
        "INSERT INTO schema_migrations (filename) VALUES (%s)",
        (sql_file.name,),
    )


def run_migrations() -> int:
    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        print("No migration files found.")
        return 0

    conn = get_db_connection()
    conn.autocommit = False
    try:
        with conn.cursor() as cursor:
            ensure_migrations_table(cursor)
            already_applied = applied_migrations(cursor)

            for sql_file in sql_files:
                if sql_file.name in already_applied:
                    print(f"Skip: {sql_file.name}")
                    continue

                print(f"Applying: {sql_file.name}")
                apply_migration(cursor, sql_file)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print("Migrations complete.")
    return 0


def main() -> None:
    try:
        raise SystemExit(run_migrations())
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
