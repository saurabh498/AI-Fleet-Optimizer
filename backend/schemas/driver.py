from datetime import datetime

from pydantic import BaseModel, Field


class DriverCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    user_id: int | None = None
    assigned_truck_id: int | None = None
    availability_status: str = Field(
        default="available",
        pattern="^(available|on_duty|resting|off_duty|inactive)$",
    )
    current_latitude: float | None = None
    current_longitude: float | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None
    accumulated_driving_minutes: int = Field(default=0, ge=0)
    accumulated_since_last_rest_minutes: int = Field(default=0, ge=0)
    last_rest_time: datetime | None = None
    rest_required: bool = False


class DriverUpdate(BaseModel):
    display_name: str | None = None
    assigned_truck_id: int | None = None
    availability_status: str | None = None
    current_latitude: float | None = None
    current_longitude: float | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None
    accumulated_driving_minutes: int | None = Field(default=None, ge=0)
    accumulated_since_last_rest_minutes: int | None = Field(default=None, ge=0)
    last_rest_time: datetime | None = None
    rest_required: bool | None = None


class DriverResponse(BaseModel):
    driver_id: int
    user_id: int | None
    assigned_truck_id: int | None
    display_name: str
    availability_status: str
    current_latitude: float | None
    current_longitude: float | None
    shift_start: datetime | None
    shift_end: datetime | None
    accumulated_driving_minutes: int
    accumulated_since_last_rest_minutes: int
    last_rest_time: datetime | None
    rest_required: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DriverFeasibilityRequest(BaseModel):
    truck_id: int
    estimated_trip_minutes: int = Field(ge=1)


class DriverFeasibilityResponse(BaseModel):
    feasible: bool
    reason: str
    requires_review: bool
    missing_data: list[str]
    rules_verified_against_law: bool

class DriverAssignRequest(BaseModel):
    truck_id: int


class DriverRestTakenResponse(BaseModel):
    driver_id: int
    last_rest_time: str
    accumulated_since_last_rest_minutes: int
    rest_required: bool