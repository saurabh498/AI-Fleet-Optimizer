from pydantic import BaseModel, Field


class WaitingTimePredictionRequest(BaseModel):
    truck_id: int
    city: str
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    available_loads: int = Field(ge=0)
    completed_loads: int = Field(ge=0)
    average_demand: float = Field(ge=0)


class WaitingTimePredictionResponse(BaseModel):
    predicted_waiting_time: float
    model_name: str
    model_version: str