"""
Cost model for truck trips.

Computes a realistic cost breakdown (fuel + driver + toll +
maintenance) based on:
    - distance in km
    - truck class (HCV / MCV / LCV / default)
    - tunable rates from config/cost_model.yaml

The model returns an explicit breakdown so downstream UI
and analytics can show where the money is going.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml


CONFIG_PATH = Path("config/cost_model.yaml")


# -------------------------------------------------
# Config loading
# -------------------------------------------------

@lru_cache(maxsize=1)
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Cost model config not found at {CONFIG_PATH}. "
            "Expected file with keys: defaults, truck_classes, emissions."
        )
    with CONFIG_PATH.open(encoding="utf-8-sig") as handle:
        return yaml.safe_load(handle)


# -------------------------------------------------
# Truck class resolution
# -------------------------------------------------

def resolve_truck_class(truck_type: Optional[str]) -> str:
    """
    Map a raw truck_type string to a known class in the config.
    Falls back to 'default' when the type is None or unknown.
    """
    config = load_config()
    classes = config["truck_classes"]

    if truck_type and truck_type in classes:
        return truck_type

    return "default"


def get_mileage_km_per_litre(truck_type: Optional[str]) -> float:
    config = load_config()
    cls = resolve_truck_class(truck_type)
    return float(config["truck_classes"][cls]["mileage_km_per_litre"])


# -------------------------------------------------
# Cost per km (all-in)
# -------------------------------------------------

def get_cost_per_km(truck_type: Optional[str] = None) -> float:
    """
    Total operational cost per km for this truck class.
    Combines fuel + driver + toll + maintenance.
    """
    config = load_config()
    defaults = config["defaults"]

    mileage = get_mileage_km_per_litre(truck_type)

    fuel_per_km = defaults["fuel_price_per_litre_inr"] / mileage
    driver_per_km = defaults["driver_cost_per_km_inr"]
    toll_per_km = defaults["toll_cost_per_km_inr"]
    maintenance_per_km = defaults["maintenance_cost_per_km_inr"]

    return round(
        fuel_per_km + driver_per_km + toll_per_km + maintenance_per_km,
        4,
    )


# -------------------------------------------------
# Full cost estimate
# -------------------------------------------------

def estimate_trip_cost(
    distance_km: float,
    truck_type: Optional[str] = None,
) -> dict:
    """
    Return a breakdown of the trip cost.

    Args:
        distance_km: total road distance
        truck_type: e.g. 'HCV', 'LCV', or None for default

    Returns:
        {
            "truck_class": str,
            "mileage_km_per_litre": float,
            "distance_km": float,
            "fuel_litres": float,
            "fuel_cost": float,
            "driver_cost": float,
            "toll_cost": float,
            "maintenance_cost": float,
            "total_cost": float,
            "cost_per_km": float,
        }
    """
    if distance_km < 0:
        raise ValueError("distance_km must be non-negative")

    config = load_config()
    defaults = config["defaults"]

    cls = resolve_truck_class(truck_type)
    mileage = get_mileage_km_per_litre(truck_type)

    fuel_litres = distance_km / mileage
    fuel_cost = fuel_litres * defaults["fuel_price_per_litre_inr"]
    driver_cost = distance_km * defaults["driver_cost_per_km_inr"]
    toll_cost = distance_km * defaults["toll_cost_per_km_inr"]
    maintenance_cost = distance_km * defaults["maintenance_cost_per_km_inr"]

    total = fuel_cost + driver_cost + toll_cost + maintenance_cost

    return {
        "truck_class": cls,
        "mileage_km_per_litre": mileage,
        "distance_km": round(distance_km, 3),
        "fuel_litres": round(fuel_litres, 3),
        "fuel_cost": round(fuel_cost, 2),
        "driver_cost": round(driver_cost, 2),
        "toll_cost": round(toll_cost, 2),
        "maintenance_cost": round(maintenance_cost, 2),
        "total_cost": round(total, 2),
        "cost_per_km": round(total / distance_km, 4) if distance_km > 0 else 0.0,
    }


def estimate_trip_cost_total(
    distance_km: float,
    truck_type: Optional[str] = None,
) -> float:
    """Convenience: just the total trip cost in INR."""
    return estimate_trip_cost(distance_km, truck_type)["total_cost"]
