# Audio Memory Map 

A spatial audio mapping application that allows users to record or upload voice memories, attach them to geographic coordinates, transcribe them, and visualize them on an interactive map.

This application is built using a **Streamlit** frontend and a **FastAPI** backend, featuring a unified, modular storage engine that supports local development and transitions seamlessly to cloud deployment (AWS S3 & PostgreSQL/pgvector).

---

## Architecture Overview

```
Streamlit UI (Port 8501)
     ↓ (HTTP requests)
FastAPI Backend (Port 8000)
     ↓ (Unified Storage Engine)
┌─────────────────────────────────┐
│           Storage Layer         │
├────────────────┬────────────────┤
│  Local Mode    │  Cloud Mode    │
│  - JSON DB     │  - PostgreSQL  │
│  - Local Disk  │  - AWS S3      │
└────────────────┴────────────────┘
```

---

## Project Structure

```
├── backend/
│   ├── main.py             # FastAPI application and route definitions
│   ├── models/             # Pydantic schemas (signals, regions)
│   ├── db/                 # SQL migrations and migrate runner
│   └── storage.py          # Unified Local/Cloud Storage controller
├── docker-compose.yml      # Local Postgres + PostGIS for cloud dev
├── Makefile                # db-up, migrate, and smoke-test helpers
├── frontend/
│   └── streamlit_app.py    # Streamlit dashboard and interactive folium map
├── data/                   # Local database directory (JSON)
├── uploads/                # Local raw audio uploads folder
├── .env.example            # Environment configurations template
├── .env                    # Active configurations (ignored by git)
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

---

## Quick Start

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your machine.

### 2. Setup Dependencies
Create a virtual environment and install the required libraries:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Install is much faster when `pip` is up to date (older pip may try to compile `pyarrow` from source). The main app only needs Streamlit and FastAPI — `gradio` is optional for legacy prototypes in `requirements-legacy.txt`.

### 3. Environment Configurations
Configure your storage choices. Copy the example configuration template:
```bash
cp .env.example .env
```
By default, the application runs in `LOCAL` mode, using local files and JSON directories. 

To use cloud storage, set `STORAGE_TYPE=CLOUD` in your `.env` and fill out your **AWS S3** and **PostgreSQL** credentials.

### Cloud mode local dev

Run PostgreSQL with PostGIS locally via Docker before using `STORAGE_TYPE=CLOUD`:

```bash
# Start Postgres + PostGIS
make db-up

# Wait until ready, then apply SQL migrations
make migrate
```

This uses the `postgis/postgis:15-3.4` image defined in `docker-compose.yml` and applies files from `backend/db/migrations/` in order. Set in your `.env`:

```bash
STORAGE_TYPE=CLOUD
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/disaster_signals
```

Useful commands:

| Command | Purpose |
|---------|---------|
| `make db-up` | Start the database container |
| `make db-down` | Stop containers |
| `make db-logs` | Tail database logs |
| `make db-ready` | Check Postgres health |
| `make migrate` | Apply pending SQL migrations |
| `make db-smoke` | Start DB, migrate, verify PostGIS |

Migration tracking uses a `schema_migrations` table so each `.sql` file runs once. Install dev dependencies first: `pip install -r requirements-dev.txt`.

### 4. Running the App

Run the FastAPI backend:
```bash
uvicorn backend.main:app --reload --port 8000
```

In a separate terminal window, start the Streamlit frontend:
```bash
streamlit run frontend/streamlit_app.py
```

Open your browser to [http://localhost:8501](http://localhost:8501) to explore your Audio Memory Map.

---

## API Endpoints

- **`GET /health`**: Health check.
- **`GET /memories`**: Retrieves a list of all memories with coordinates, transcripts, and audio references.
- **`POST /memories`**: Uploads a new memory (receives form data: `title`, `lat`, `lon`, `transcript` along with the binary `audio` file).
- **`GET /memories/{audio_ref}/audio`**: Streams the raw audio file.
