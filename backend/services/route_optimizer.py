from math import radians, sin, cos, sqrt, atan2
from typing import Optional

from sqlalchemy.orm import Session

from backend.services.routing import get_route_km
from backend.services.cost_model import estimate_trip_cost
from backend.services.emissions import estimate_co2


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    '''
    Straight-line (haversine) distance in km.
    Retained as a fallback and for tests.
    '''
    earth_radius_km = 6371.0

    lat1 = radians(latitude1)
    lon1 = radians(longitude1)
    lat2 = radians(latitude2)
    lon2 = radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(earth_radius_km * c, 2)


def _road_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    db: Optional[Session]
) -> float:
    '''Road distance via OSRM (cached), falling back to haversine.'''
    if db is None:
        return calculate_distance_km(lat1, lon1, lat2, lon2)
    return get_route_km(lat1, lon1, lat2, lon2, db=db)


def calculate_route_distances(
    truck_latitude: float,
    truck_longitude: float,
    pickup_latitude: float,
    pickup_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    truck_type: Optional[str] = None,
    db: Optional[Session] = None
) -> dict:
    '''
    Calculate pickup + delivery distances, total trip cost,
    and CO2 emissions.

    Cost and CO2 come from the cost_model / emissions services,
    driven by truck_type (HCV / MCV / LCV / default).
    '''

    pickup_distance = _road_distance_km(
        truck_latitude, truck_longitude,
        pickup_latitude, pickup_longitude,
        db,
    )

    delivery_distance = _road_distance_km(
        pickup_latitude, pickup_longitude,
        destination_latitude, destination_longitude,
        db,
    )

    total_distance = round(pickup_distance + delivery_distance, 2)

    cost = estimate_trip_cost(total_distance, truck_type)
    co2 = estimate_co2(total_distance, truck_type)

    return {
        "pickup_distance_km": round(pickup_distance, 2),
        "delivery_distance_km": round(delivery_distance, 2),
        "total_distance_km": total_distance,
        "estimated_cost": cost["total_cost"],
        "cost_breakdown": cost,
        "co2_kg": co2["co2_kg"],
        "co2_breakdown": co2,
    }


def calculate_route_efficiency(
    revenue: float,
    total_distance_km: float,
    estimated_cost: float
) -> dict:
    '''Unchanged — takes total cost and computes efficiency.'''

    estimated_profit = round(revenue - estimated_cost, 2)

    if revenue <= 0:
        efficiency_score = 0
    else:
        profit_margin = (estimated_profit / revenue) * 100
        efficiency_score = round(max(0, min(100, profit_margin)), 2)

    if efficiency_score >= 70:
        recommendation = "Excellent"
    elif efficiency_score >= 40:
        recommendation = "Good"
    elif efficiency_score >= 20:
        recommendation = "Moderate"
    else:
        recommendation = "Poor"

    return {
        "estimated_profit": estimated_profit,
        "efficiency_score": efficiency_score,
        "recommendation": recommendation
    }
