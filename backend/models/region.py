from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


class RegionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    default_language: str = Field(default="en", min_length=2, max_length=10)

    @model_validator(mode="after")
    def validate_bbox(self) -> "RegionCreate":
        if self.min_lat >= self.max_lat:
            raise ValueError("min_lat must be less than max_lat")
        if self.min_lon >= self.max_lon:
            raise ValueError("min_lon must be less than max_lon")
        return self

    def contains_point(self, lat: float, lon: float) -> bool:
        return (
            self.min_lat <= lat <= self.max_lat
            and self.min_lon <= lon <= self.max_lon
        )


class RegionResponse(BaseModel):
    id: UUID
    name: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    default_language: str
    created_at: datetime

    @classmethod
    def from_create(cls, payload: RegionCreate, region_id: Optional[UUID] = None) -> "RegionResponse":
        return cls(
            id=region_id or uuid4(),
            name=payload.name,
            min_lat=payload.min_lat,
            max_lat=payload.max_lat,
            min_lon=payload.min_lon,
            max_lon=payload.max_lon,
            default_language=payload.default_language,
            created_at=datetime.now(timezone.utc),
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                    "name": "Pilot Region",
                    "min_lat": 18.4,
                    "max_lat": 18.6,
                    "min_lon": -72.4,
                    "max_lon": -72.2,
                    "default_language": "ht",
                    "created_at": "2026-06-07T12:00:00Z",
                }
            ]
        }
    }
