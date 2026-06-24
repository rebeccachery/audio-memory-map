from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
REGION_ID = str(uuid4())


def test_openapi_includes_signal_and_region_schemas():
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema_names = response.json()["components"]["schemas"].keys()
    assert "SignalCreate" in schema_names
    assert "SignalResponse" in schema_names
    assert "RegionCreate" in schema_names
    assert "RegionResponse" in schema_names
    assert "SignalFilters" in schema_names


def test_validate_signal_returns_response_shape():
    response = client.post(
        "/signals/validate",
        json={
            "region_id": REGION_ID,
            "type": "need",
            "urgency": "critical",
            "lat": 18.5,
            "lon": -72.3,
            "transcript": "Need water",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "need"
    assert body["urgency"] == "critical"
    assert body["title"] == "Need water"
    assert body["audio_ref"] == "preview.wav"


def test_validate_signal_rejects_invalid_type_with_422():
    response = client.post(
        "/signals/validate",
        json={
            "region_id": REGION_ID,
            "type": "unknown",
            "lat": 18.5,
            "lon": -72.3,
        },
    )

    assert response.status_code == 422


def test_validate_region_rejects_invalid_bbox_with_422():
    response = client.post(
        "/regions/validate",
        json={
            "name": "Invalid Region",
            "min_lat": 18.6,
            "max_lat": 18.4,
            "min_lon": -72.4,
            "max_lon": -72.2,
        },
    )

    assert response.status_code == 422
