from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class SignalType(str, Enum):
    NEED = "need"
    UPDATE = "update"
    HAZARD = "hazard"
    RESOURCE = "resource"
    STATUS = "status"


class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    INFO = "info"


class SignalStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    STALE = "stale"


class SignalCreate(BaseModel):
    region_id: UUID
    type: SignalType
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    accuracy_m: Optional[float] = Field(default=None, gt=0)
    title: Optional[str] = Field(default=None, max_length=200)
    transcript: Optional[str] = None
    client_id: Optional[str] = Field(default=None, max_length=128)
    local_id: Optional[str] = Field(default=None, max_length=128)
    captured_at: Optional[datetime] = None
    captured_offline: bool = False
    categories: list[str] = Field(default_factory=list)

    @field_validator("categories")
    @classmethod
    def normalize_categories(cls, value: list[str]) -> list[str]:
        return [category.strip().lower() for category in value if category.strip()]


class SignalResponse(BaseModel):
    id: UUID
    region_id: UUID
    type: SignalType
    urgency: UrgencyLevel
    status: SignalStatus
    title: Optional[str]
    lat: float
    lon: float
    accuracy_m: Optional[float]
    audio_ref: str
    audio_duration_s: Optional[float] = None
    language_detected: Optional[str] = None
    transcript_original: str = ""
    categories: list[str] = Field(default_factory=list)
    reporter_hash: Optional[str] = None
    client_id: Optional[str] = None
    local_id: Optional[str] = None
    captured_at: Optional[datetime] = None
    captured_offline: bool = False
    created_at: datetime
    synced_at: datetime
    embedding: list[float] = Field(default_factory=list)

    @classmethod
    def from_create(
        cls,
        payload: SignalCreate,
        *,
        audio_ref: str,
        transcript_original: str = "",
        language_detected: Optional[str] = None,
        audio_duration_s: Optional[float] = None,
        signal_id: Optional[UUID] = None,
        status: SignalStatus = SignalStatus.PENDING,
        embedding: Optional[list[float]] = None,
    ) -> "SignalResponse":
        now = datetime.now(timezone.utc)
        captured_at = payload.captured_at or now
        title = payload.title or transcript_original[:60].strip() or f"{payload.type.value} signal"

        return cls(
            id=signal_id or uuid4(),
            region_id=payload.region_id,
            type=payload.type,
            urgency=payload.urgency,
            status=status,
            title=title,
            lat=payload.lat,
            lon=payload.lon,
            accuracy_m=payload.accuracy_m,
            audio_ref=audio_ref,
            audio_duration_s=audio_duration_s,
            language_detected=language_detected,
            transcript_original=transcript_original or payload.transcript or "",
            categories=payload.categories,
            client_id=payload.client_id,
            local_id=payload.local_id,
            captured_at=captured_at,
            captured_offline=payload.captured_offline,
            created_at=now,
            synced_at=now,
            embedding=embedding or [],
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "region_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                    "type": "need",
                    "urgency": "critical",
                    "status": "pending",
                    "title": "Need clean water near market",
                    "lat": 18.5,
                    "lon": -72.3,
                    "accuracy_m": 25.0,
                    "audio_ref": "abc123.wav",
                    "audio_duration_s": 12.5,
                    "language_detected": "ht",
                    "transcript_original": "Nou bezwen dlo nan mache a.",
                    "categories": ["water"],
                    "client_id": "device-001",
                    "local_id": "local-001",
                    "captured_at": "2026-06-07T14:30:00Z",
                    "captured_offline": True,
                    "created_at": "2026-06-07T14:31:00Z",
                    "synced_at": "2026-06-07T14:31:00Z",
                    "embedding": [],
                }
            ]
        }
    }


class SignalFilters(BaseModel):
    region_id: Optional[UUID] = None
    since: Optional[datetime] = None
    type: Optional[SignalType] = None
    urgency: Optional[UrgencyLevel] = None
    status: Optional[SignalStatus] = None
    min_lat: Optional[float] = Field(default=None, ge=-90, le=90)
    max_lat: Optional[float] = Field(default=None, ge=-90, le=90)
    min_lon: Optional[float] = Field(default=None, ge=-180, le=180)
    max_lon: Optional[float] = Field(default=None, ge=-180, le=180)
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_bbox(self) -> "SignalFilters":
        bbox_values = [self.min_lat, self.max_lat, self.min_lon, self.max_lon]
        if any(value is not None for value in bbox_values) and not all(
            value is not None for value in bbox_values
        ):
            raise ValueError("bbox filters require min_lat, max_lat, min_lon, and max_lon")

        if self.min_lat is not None and self.max_lat is not None and self.min_lat >= self.max_lat:
            raise ValueError("min_lat must be less than max_lat")

        if self.min_lon is not None and self.max_lon is not None and self.min_lon >= self.max_lon:
            raise ValueError("min_lon must be less than max_lon")

        return self
