from pydantic import BaseModel


class InternalSearchSummary(BaseModel):
    candidates_considered: int
    feasible_matches: int
    best_match_available: bool


class PreferredRoute(BaseModel):
    pickup_city: str | None
    destination_city: str | None
    distance_km: float | None
    match_score: float | None
    route_efficiency_score: float | None


class SearchBriefDetails(BaseModel):
    truck_type: str
    capacity_kg: float
    current_load_kg: float
    remaining_capacity_kg: float
    current_city: str | None
    current_latitude: float | None
    current_longitude: float | None
    position_source: str
    availability: str
    preferred_routes: list[PreferredRoute]
    max_weight_kg: float


class SearchBriefResponse(BaseModel):
    truck_id: int
    generated_at: str
    internal_search_summary: InternalSearchSummary
    external_search_recommended: bool
    brief: SearchBriefDetails
    privacy_note: str
    generated_text: str
