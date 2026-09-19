'''
4-way fleet assignment benchmark.

Strategies:
    1. nearest          - minimize pickup distance
    2. greedy_profit    - maximize raw shipment revenue
    3. ortools_rules    - maximize rule-based match_score
    4. ai               - maximize carbon-adjusted profit + ML bonus

The AI strategy is multi-objective:
    effective_value = profit - carbon_price * co2_kg
    ai_score        = effective_value + ml_adjustment * ml_rupee_per_point
'''

from functools import lru_cache
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.truck import Truck
from backend.services.backhaul_matching import find_backhaul_matches
from backend.services.ml_decision_context import (
    build_ml_decision_context,
    build_ml_context_for_city,
)
from backend.services.assignment_decision import calculate_ml_adjustment


STRATEGIES = ["nearest", "greedy_profit", "ortools_rules", "ai"]


# -------------------------------------------------
# Benchmark config
# -------------------------------------------------

@lru_cache(maxsize=1)
def _benchmark_config() -> dict:
    from backend.services.cost_model import load_config
    return load_config().get("benchmark", {})


def _carbon_price() -> float:
    return float(_benchmark_config().get("carbon_price_inr_per_kg", 8.0))


def _ml_rupee_per_point() -> float:
    return float(_benchmark_config().get("ml_rupee_per_point", 300.0))


# -------------------------------------------------
# Scoring
# -------------------------------------------------

def _score(strategy: str, candidate: dict) -> float:
    if strategy == "nearest":
        return -candidate["distance_km"]

    if strategy == "greedy_profit":
        return candidate["revenue"]

    if strategy == "ortools_rules":
        return candidate["match_score"]

    if strategy == "ai":
        co2 = candidate.get("co2_kg", 0) or 0
        profit = candidate.get("profit", 0)
        ml_adj = candidate.get("ml_adjustment", 0)

        effective_value = profit - _carbon_price() * co2
        ml_bonus = ml_adj * _ml_rupee_per_point()
        return effective_value + ml_bonus

    raise ValueError(f"Unknown strategy: {strategy}")


# -------------------------------------------------
# One-to-one assignment
# -------------------------------------------------

def _one_to_one_assign(candidates: list, strategy: str) -> list:
    ranked = sorted(
        candidates,
        key=lambda c: _score(strategy, c),
        reverse=True,
    )

    used_trucks = set()
    used_shipments = set()
    assignments = []

    for c in ranked:
        if c["truck_id"] in used_trucks:
            continue
        if c["load_id"] in used_shipments:
            continue
        assignments.append(c)
        used_trucks.add(c["truck_id"])
        used_shipments.add(c["load_id"])

    return assignments


# -------------------------------------------------
# Aggregation
# -------------------------------------------------

def _aggregate(assignments: list) -> dict:
    if not assignments:
        return {
            "trucks_assigned": 0,
            "total_distance_km": 0.0,
            "total_cost_inr": 0.0,
            "total_revenue_inr": 0.0,
            "total_profit_inr": 0.0,
            "total_co2_kg": 0.0,
            "avg_route_efficiency": 0.0,
            "avg_match_score": 0.0,
        }

    n = len(assignments)

    return {
        "trucks_assigned": n,
        "total_distance_km": round(sum(c["distance_km"] for c in assignments), 2),
        "total_cost_inr": round(sum(c["cost"] for c in assignments), 2),
        "total_revenue_inr": round(sum(c["revenue"] for c in assignments), 2),
        "total_profit_inr": round(sum(c["profit"] for c in assignments), 2),
        "total_co2_kg": round(sum(c["co2_kg"] for c in assignments), 2),
        "avg_route_efficiency": round(
            sum(c["route_efficiency_score"] for c in assignments) / n, 2
        ),
        "avg_match_score": round(
            sum(c["match_score"] for c in assignments) / n, 2
        ),
    }


# -------------------------------------------------
# Candidate construction
# -------------------------------------------------

def _candidate_from_match(
    truck_id: int,
    match: dict,
    ml_adjustment: float,
) -> dict:
    route = match.get("route", {})
    base_score = match.get("match_score", 0)

    return {
        "truck_id": truck_id,
        "load_id": match["load_id"],
        "pickup_city": match.get("pickup_city"),
        "destination_city": match.get("destination_city"),
        "distance_km": (
            route.get("total_distance_km")
            or match.get("distance_to_pickup_km", 0)
        ),
        "cost": match.get("estimated_route_cost", 0),
        "revenue": match.get("revenue", 0),
        "profit": match.get("estimated_route_profit", 0),
        "co2_kg": match.get("co2_kg", 0),
        "route_efficiency_score": match.get("route_efficiency_score", 0),
        "match_score": base_score,
        "ml_adjustment": ml_adjustment,
        "ml_adjusted_decision_score": round(base_score + ml_adjustment, 2),
    }


# -------------------------------------------------
# Main entry
# -------------------------------------------------

def benchmark_fleet(
    db: Session,
    truck_ids: Optional[list] = None,
) -> dict:
    '''Run all 4 strategies on the current fleet + shipment pool.'''

    if truck_ids is None:
        trucks = db.query(Truck).filter(Truck.status == "available").all()
    else:
        trucks = db.query(Truck).filter(Truck.truck_id.in_(truck_ids)).all()

    candidates = []

    # Cache destination-city ML adjustment so we don't recompute
    # the same city's demand context 50 times.
    ml_by_city_cache: dict = {}

    def _ml_adjustment_for_destination(city: str) -> float:
        if not city:
            return 0.0
        if city in ml_by_city_cache:
            return ml_by_city_cache[city]
        try:
            ctx = build_ml_context_for_city(city, db)
            adj = calculate_ml_adjustment(
                predicted_demand=ctx.get("predicted_demand", 0.0),
                predicted_waiting_time=ctx.get("predicted_waiting_time", 0.0),
            )
        except Exception:
            adj = 0.0
        ml_by_city_cache[city] = adj
        return adj

    for truck in trucks:
        result = find_backhaul_matches(truck.truck_id, db)
        if result is None:
            continue

        for match in result.get("matches", []):
            # Per-candidate ML: based on the shipment's destination city,
            # not the truck's current city.
            dest_city = match.get("destination_city")
            ml_adjustment = _ml_adjustment_for_destination(dest_city)

            candidates.append(
                _candidate_from_match(truck.truck_id, match, ml_adjustment)
            )

    results = {}
    for strategy in STRATEGIES:
        assignments = _one_to_one_assign(candidates, strategy)
        results[strategy] = {
            "metrics": _aggregate(assignments),
            "assignments": assignments,
        }

    baseline_keys = ["nearest", "greedy_profit", "ortools_rules"]
    ai_metrics = results["ai"]["metrics"]

    improvements = {}
    for key in baseline_keys:
        m = results[key]["metrics"]

        def pct(baseline, current, invert=False):
            if baseline == 0:
                return 0.0
            raw = (baseline - current) / baseline * 100
            return round(raw if not invert else -raw, 2)

        improvements[f"vs_{key}"] = {
            "distance_reduction_pct": pct(
                m["total_distance_km"], ai_metrics["total_distance_km"]
            ),
            "cost_reduction_pct": pct(
                m["total_cost_inr"], ai_metrics["total_cost_inr"]
            ),
            "co2_reduction_pct": pct(
                m["total_co2_kg"], ai_metrics["total_co2_kg"]
            ),
            "profit_change_pct": pct(
                m["total_profit_inr"], ai_metrics["total_profit_inr"], invert=True
            ),
        }

    return {
        "trucks_evaluated": len(trucks),
        "candidates_considered": len(candidates),
        "config": {
            "carbon_price_inr_per_kg": _carbon_price(),
            "ml_rupee_per_point": _ml_rupee_per_point(),
        },
        "results": results,
        "improvements": improvements,
    }
