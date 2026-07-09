POSTGRES_URL ?= postgresql://postgres:postgres@127.0.0.1:5432/disaster_signals
PYTHON ?= ./venv/bin/python
# Project root must be on PYTHONPATH so `backend` imports resolve
export PYTHONPATH := $(CURDIR)

.PHONY: setup-dev check-dev-deps db-up db-down db-logs db-ready db-wait migrate db-smoke

setup-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

check-dev-deps:
	@$(PYTHON) -c "import psycopg2" 2>/dev/null || \
		(echo "Missing psycopg2. Install dev dependencies with:" && \
		 echo "  make setup-dev" && \
		 echo "or: ./venv/bin/pip install -r requirements-dev.txt" && \
		 exit 1)

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-logs:
	docker compose logs -f db

db-ready:
	docker compose exec db pg_isready -U postgres -d disaster_signals

db-wait:
	@POSTGRES_URL=$(POSTGRES_URL) $(PYTHON) -c "import os, sys, time; \
import psycopg2; \
url = os.environ['POSTGRES_URL']; \
\
for attempt in range(1, 11): \
    try: \
        psycopg2.connect(url).close(); \
        print('Postgres is ready.'); \
        sys.exit(0); \
    except psycopg2.OperationalError: \
        if attempt == 10: \
            print('Cannot connect to Postgres at', url, file=sys.stderr); \
            print('Try: make db-up', file=sys.stderr); \
            print('Then wait a few seconds and run: make db-ready', file=sys.stderr); \
            sys.exit(1); \
        print(f'Waiting for Postgres ({attempt}/10)...'); \
        time.sleep(2)"

migrate: check-dev-deps db-wait
	POSTGRES_URL=$(POSTGRES_URL) $(PYTHON) -m backend.db

db-smoke: db-up
	@echo "Waiting for Postgres..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		docker compose exec db pg_isready -U postgres -d disaster_signals && break; \
		sleep 2; \
	done
	$(MAKE) migrate
	@docker compose exec db psql -U postgres -d disaster_signals -c "SELECT PostGIS_Version();"
	@docker compose exec db psql -U postgres -d disaster_signals -c "\dt"
