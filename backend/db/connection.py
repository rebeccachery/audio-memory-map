import os

import psycopg2
from psycopg2.extensions import connection as Connection


def get_db_connection() -> Connection:
    """Return a PostgreSQL connection using POSTGRES_URL."""
    db_url = os.getenv("POSTGRES_URL")
    if not db_url:
        raise RuntimeError("POSTGRES_URL is not set")
    return psycopg2.connect(db_url)
