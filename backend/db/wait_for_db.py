"""Wait until Postgres accepts connections."""

import os
import sys
import time

import psycopg2


def main() -> int:
    url = os.environ.get("POSTGRES_URL")
    if not url:
        print("POSTGRES_URL is not set", file=sys.stderr)
        return 1

    for attempt in range(1, 11):
        try:
            psycopg2.connect(url).close()
            print("Postgres is ready.")
            return 0
        except psycopg2.OperationalError:
            if attempt == 10:
                print(f"Cannot connect to Postgres at {url}", file=sys.stderr)
                print("Try: make db-up", file=sys.stderr)
                print("Then wait a few seconds and run: make db-ready", file=sys.stderr)
                return 1
            print(f"Waiting for Postgres ({attempt}/10)...")
            time.sleep(2)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
