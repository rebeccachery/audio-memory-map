from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.models import (
    RegionCreate,
    RegionResponse,
    SignalCreate,
    SignalFilters,
    SignalResponse,
    SignalType,
    UrgencyLevel,
)


REGION_ID = uuid4()


def test_signal_create_accepts_valid_payload():
    signal = SignalCreate(
        region_id=REGION_ID,
        type=SignalType.NEED,
        lat=18.5,
        lon=-72.3,
        urgency=UrgencyLevel.CRITICAL,
        categories=[" Water ", "medical"],
    )

    assert signal.type == SignalType.NEED
    assert signal.categories == ["water", "medical"]


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("type", "unknown"),
        ("urgency", "urgent"),
    ],
)
def test_signal_create_rejects_invalid_enums(field_name, value):
    payload = {
        "region_id": REGION_ID,
        "type": "need",
        "lat": 18.5,
        "lon": -72.3,
        field_name: value,
    }

    with pytest.raises(ValidationError):
        SignalCreate(**payload)


@pytest.mark.parametrize(
    "lat, lon",
    [
        (91, 0),
        (-91, 0),
        (0, 181),
        (0, -181),
    ],
)
def test_signal_create_rejects_invalid_coordinates(lat, lon):
    with pytest.raises(ValidationError):
        SignalCreate(
            region_id=REGION_ID,
            type=SignalType.UPDATE,
            lat=lat,
            lon=lon,
        )


def test_signal_response_from_create_builds_title_from_transcript():
    payload = SignalCreate(
        region_id=REGION_ID,
        type=SignalType.NEED,
        lat=18.5,
        lon=-72.3,
    )

    response = SignalResponse.from_create(
        payload,
        audio_ref="sample.wav",
        transcript_original="Need water near the school building",
    )

    assert response.title == "Need water near the school building"
    assert response.transcript_original == "Need water near the school building"
    assert response.audio_ref == "sample.wav"
    assert response.status.value == "pending"


def test_region_create_rejects_invalid_bbox():
    with pytest.raises(ValidationError):
        RegionCreate(
            name="Invalid Region",
            min_lat=18.6,
            max_lat=18.4,
            min_lon=-72.4,
            max_lon=-72.2,
        )


def test_region_create_contains_point():
    region = RegionCreate(
        name="Pilot Region",
        min_lat=18.4,
        max_lat=18.6,
        min_lon=-72.4,
        max_lon=-72.2,
    )

    assert region.contains_point(18.5, -72.3) is True
    assert region.contains_point(19.0, -72.3) is False


def test_region_response_from_create():
    payload = RegionCreate(
        name="Pilot Region",
        min_lat=18.4,
        max_lat=18.6,
        min_lon=-72.4,
        max_lon=-72.2,
        default_language="ht",
    )

    response = RegionResponse.from_create(payload)

    assert response.name == "Pilot Region"
    assert response.default_language == "ht"
    assert response.created_at.tzinfo is not None


def test_signal_filters_require_complete_bbox():
    with pytest.raises(ValidationError):
        SignalFilters(region_id=REGION_ID, min_lat=18.4)


def test_signal_filters_reject_inverted_bbox():
    with pytest.raises(ValidationError):
        SignalFilters(
            region_id=REGION_ID,
            min_lat=18.6,
            max_lat=18.4,
            min_lon=-72.4,
            max_lon=-72.2,
        )


def test_signal_create_accepts_captured_at_timestamp():
    captured_at = datetime(2026, 6, 7, 14, 30, tzinfo=timezone.utc)
    signal = SignalCreate(
        region_id=REGION_ID,
        type=SignalType.STATUS,
        lat=18.5,
        lon=-72.3,
        captured_at=captured_at,
        captured_offline=True,
        client_id="device-001",
        local_id="local-001",
    )

    assert signal.captured_at == captured_at
    assert signal.captured_offline is True
