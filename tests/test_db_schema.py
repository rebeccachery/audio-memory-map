from pathlib import Path


MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "backend" / "db" / "migrations"


def test_signals_and_regions_migration_defines_core_tables():
    sql = (MIGRATIONS_DIR / "002_signals_and_regions.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE regions" in sql
    assert "CREATE TABLE signals" in sql
    assert "signals_client_local_unique" in sql
    assert "signals_geom_idx" in sql
    assert "REFERENCES regions(id)" in sql
    assert "CREATE TABLE IF NOT EXISTS memories" not in sql


def test_migration_files_are_ordered():
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    names = [path.name for path in migration_files]

    assert names == ["001_init_postgis.sql", "002_signals_and_regions.sql"]
