from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TruckLocationCreate(BaseModel):
    truck_id: int
    timestamp: datetime
    latitude: float
    longitude: float
    speed: float | None = None


class TruckLocationResponse(TruckLocationCreate):
    location_id: int

    model_config = ConfigDict(from_attributes=True)