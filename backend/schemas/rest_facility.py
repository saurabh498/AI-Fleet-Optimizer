from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


FACILITY_TYPES = ('apna_ghar', 'wayside_amenity', 'other_verified')
VERIFICATION_STATUSES = ('pending', 'verified', 'retired')


class RestFacilityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    facility_type: Literal['apna_ghar', 'wayside_amenity', 'other_verified']
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str | None = None
    road_reference: str | None = None
    available_amenities: str | None = None
    source_url: str = Field(min_length=1, max_length=500)
    source_date: date
    verification_status: Literal['pending', 'verified', 'retired'] = 'pending'
    notes: str | None = None


class RestFacilityResponse(BaseModel):
    facility_id: int
    name: str
    facility_type: str
    latitude: float
    longitude: float
    address: str | None
    road_reference: str | None
    available_amenities: str | None
    source_url: str
    source_date: date
    verification_status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class RestFacilityImportRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=200)


class RestFacilityImportResult(BaseModel):
    file: str
    total_rows: int
    created: int
    skipped_duplicates: int
    rejected: list[dict]
