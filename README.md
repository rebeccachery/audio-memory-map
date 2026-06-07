# Audio Memory Map 
![Status](https://img.shields.io/badge/status-active-brightgreen)
![Stage](https://img.shields.io/badge/stage-full--stack%20prototype-orange)
![Architecture](https://img.shields.io/badge/architecture-Streamlit%20%E2%86%92%20FastAPI-blue)
![Feature](https://img.shields.io/badge/feature-interactive%20audio%20map-teal)
![Data](https://img.shields.io/badge/data-transcripts%20%2B%20coordinates-green)
![Storage](https://img.shields.io/badge/storage-unified%20engine-purple)
![Mode](https://img.shields.io/badge/mode-local%20or%20cloud-yellow)
![Infra](https://img.shields.io/badge/infra-S3%20%2B%20pgvector-0ea5e9)

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
│   └── storage.py          # Unified Local/Cloud Storage controller
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
pip install -r requirements.txt
```

### 3. Environment Configurations
Configure your storage choices. Copy the example configuration template:
```bash
cp .env.example .env
```
By default, the application runs in `LOCAL` mode, using local files and JSON directories. 

To use cloud storage, set `STORAGE_TYPE=CLOUD` in your `.env` and fill out your **AWS S3** and **PostgreSQL** credentials.

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
