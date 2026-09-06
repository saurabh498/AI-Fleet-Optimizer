from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShipmentCreate(BaseModel):
    pickup_city: str
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None

    destination_city: str
    destination_latitude: float | None = None
    destination_longitude: float | None = None

    weight: float
    volume: float | None = None

    cargo_type: str

    pickup_start: datetime | None = None
    pickup_deadline: datetime | None = None
    delivery_deadline: datetime | None = None

    revenue: float
    status: str = "available"


class ShipmentResponse(ShipmentCreate):
    load_id: int

    model_config = ConfigDict(from_attributes=True)