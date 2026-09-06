from pydantic import BaseModel, ConfigDict


class TruckCreate(BaseModel):
    truck_type: str
    capacity: float
    current_load: float = 0
    current_latitude: float | None = None
    current_longitude: float | None = None
    current_city: str | None = None
    status: str = "available"
    destination: str | None = None
    cost_per_km: float


class TruckResponse(TruckCreate):
    truck_id: int

    model_config = ConfigDict(from_attributes=True)