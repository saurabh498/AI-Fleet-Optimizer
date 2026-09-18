"""
CO2 emissions model for truck trips.

Computed from fuel consumption (diesel) using the IPCC 2006
emission factor. Truck class mileage comes from the same config
used by the cost model, so the two stay in sync.
"""

from typing import Optional

from backend.services.cost_model import (
    get_mileage_km_per_litre,
    load_config,
    resolve_truck_class,
)


def estimate_co2(
    distance_km: float,
    truck_type: Optional[str] = None,
) -> dict:
    """
    Return CO2 breakdown for a trip.

    Args:
        distance_km: total road distance
        truck_type: e.g. 'HCV', 'LCV', or None

    Returns:
        {
            "truck_class": str,
            "distance_km": float,
            "fuel_litres": float,
            "co2_kg": float,
            "co2_per_km_kg": float,
        }
    """
    if distance_km < 0:
        raise ValueError("distance_km must be non-negative")

    config = load_config()
    co2_factor = config["emissions"]["diesel_co2_kg_per_litre"]

    cls = resolve_truck_class(truck_type)
    mileage = get_mileage_km_per_litre(truck_type)

    fuel_litres = distance_km / mileage if mileage > 0 else 0.0
    co2_kg = fuel_litres * co2_factor

    return {
        "truck_class": cls,
        "distance_km": round(distance_km, 3),
        "fuel_litres": round(fuel_litres, 3),
        "co2_kg": round(co2_kg, 3),
        "co2_per_km_kg": round(co2_kg / distance_km, 4) if distance_km > 0 else 0.0,
    }


def estimate_co2_kg(
    distance_km: float,
    truck_type: Optional[str] = None,
) -> float:
    """Convenience: just the CO2 in kg."""
    return estimate_co2(distance_km, truck_type)["co2_kg"]
