POSTGRES_URL ?= postgresql://postgres:postgres@localhost:5432/disaster_signals
PYTHON ?= ./venv/bin/python

.PHONY: db-up db-down db-logs db-ready migrate db-smoke

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-logs:
	docker compose logs -f db

db-ready:
	docker compose exec db pg_isready -U postgres -d disaster_signals

migrate:
	POSTGRES_URL=$(POSTGRES_URL) $(PYTHON) backend/db/migrate.py

db-smoke: db-up
	@echo "Waiting for Postgres..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		docker compose exec db pg_isready -U postgres -d disaster_signals && break; \
		sleep 2; \
	done
	$(MAKE) migrate
	@docker compose exec db psql -U postgres -d disaster_signals -c "SELECT PostGIS_Version();"
