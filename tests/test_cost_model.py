import pytest

from backend.services.cost_model import (
    estimate_trip_cost,
    get_cost_per_km,
    get_mileage_km_per_litre,
    resolve_truck_class,
)
from backend.services.emissions import estimate_co2, estimate_co2_kg


# -------------------------------------------------
# Cost model
# -------------------------------------------------

def test_hcv_mileage_is_lower_than_lcv():
    hcv = get_mileage_km_per_litre("HCV")
    lcv = get_mileage_km_per_litre("LCV")
    assert hcv < lcv


def test_unknown_truck_type_falls_back_to_default():
    assert resolve_truck_class("SPACESHIP") == "default"
    assert resolve_truck_class(None) == "default"


def test_cost_scales_with_distance():
    short = estimate_trip_cost(100, "HCV")["total_cost"]
    long = estimate_trip_cost(1000, "HCV")["total_cost"]
    assert long > short * 9  # ~10x distance -> ~10x cost


def test_cost_breakdown_sums_correctly():
    r = estimate_trip_cost(500, "HCV")
    component_sum = (
        r["fuel_cost"]
        + r["driver_cost"]
        + r["toll_cost"]
        + r["maintenance_cost"]
    )
    assert abs(component_sum - r["total_cost"]) < 0.01


def test_hcv_more_expensive_than_lcv_per_km():
    hcv = get_cost_per_km("HCV")
    lcv = get_cost_per_km("LCV")
    assert hcv > lcv


def test_zero_distance_cost():
    r = estimate_trip_cost(0, "HCV")
    assert r["total_cost"] == 0
    assert r["cost_per_km"] == 0


def test_negative_distance_raises():
    with pytest.raises(ValueError):
        estimate_trip_cost(-10, "HCV")


# -------------------------------------------------
# Emissions
# -------------------------------------------------

def test_hcv_emits_more_than_lcv():
    hcv = estimate_co2_kg(500, "HCV")
    lcv = estimate_co2_kg(500, "LCV")
    assert hcv > lcv


def test_emissions_scale_with_distance():
    r1 = estimate_co2_kg(100, "HCV")
    r2 = estimate_co2_kg(1000, "HCV")
    assert abs(r2 - r1 * 10) < 0.1


def test_emissions_breakdown_shape():
    r = estimate_co2(500, "HCV")
    assert "co2_kg" in r
    assert "co2_per_km_kg" in r
    assert "fuel_litres" in r
    assert r["co2_per_km_kg"] > 0


def test_negative_distance_raises_emissions():
    with pytest.raises(ValueError):
        estimate_co2(-5, "HCV")
