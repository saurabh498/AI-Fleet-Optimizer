from backend.services.benchmark import (
    STRATEGIES,
    _aggregate,
    _one_to_one_assign,
    _score,
)


def _sample_candidates():
    return [
        {"truck_id": 1, "load_id": 101, "distance_km": 50,  "profit": 1000, "revenue": 5000, "match_score": 120, "ml_adjustment": 10,  "ml_adjusted_decision_score": 130, "route_efficiency_score": 70, "cost": 2000, "co2_kg": 40},
        {"truck_id": 1, "load_id": 102, "distance_km": 200, "profit": 5000, "revenue": 9000, "match_score": 150, "ml_adjustment": -10, "ml_adjusted_decision_score": 140, "route_efficiency_score": 80, "cost": 3000, "co2_kg": 90},
        {"truck_id": 2, "load_id": 101, "distance_km": 300, "profit": 800,  "revenue": 4000, "match_score": 100, "ml_adjustment": 10,  "ml_adjusted_decision_score": 110, "route_efficiency_score": 50, "cost": 2200, "co2_kg": 75},
        {"truck_id": 2, "load_id": 102, "distance_km": 100, "profit": 3000, "revenue": 7000, "match_score": 140, "ml_adjustment": 15,  "ml_adjusted_decision_score": 155, "route_efficiency_score": 75, "cost": 2500, "co2_kg": 60},
    ]


def test_all_strategies_defined():
    for s in ["nearest", "greedy_profit", "ortools_rules", "ai"]:
        assert s in STRATEGIES


def test_nearest_picks_closest_per_truck():
    pairs = {(a["truck_id"], a["load_id"]) for a in _one_to_one_assign(_sample_candidates(), "nearest")}
    assert (1, 101) in pairs   # 50 km
    assert (2, 102) in pairs   # 100 km


def test_greedy_profit_picks_highest_revenue():
    pairs = {(a["truck_id"], a["load_id"]) for a in _one_to_one_assign(_sample_candidates(), "greedy_profit")}
    # Truck 1 should get load 102 (revenue 9000 > 5000)
    assert (1, 102) in pairs


def test_ai_strategy_uses_carbon_adjusted_profit():
    pairs = {(a["truck_id"], a["load_id"]) for a in _one_to_one_assign(_sample_candidates(), "ai")}
    # AI = (profit - carbon_price * co2) + ml_adjustment * rupee_per_point
    # with carbon_price=8, ml_rupee_per_point=300
    # T1/L102: (5000 - 720) + (-10*300) = 1280
    # T2/L102: (3000 - 480) + (15*300)  = 7020   <- highest
    # T1/L101: (1000 - 320) + (10*300)  = 3680
    # T2/L101: (800 - 600)  + (10*300)  = 3200
    # Order: T2/L102, T1/L101, T2/L101(skip truck2), T1/L102(skip truck1)
    assert (2, 102) in pairs
    assert (1, 101) in pairs


def test_one_to_one_prevents_conflicts():
    for strategy in STRATEGIES:
        assignments = _one_to_one_assign(_sample_candidates(), strategy)
        truck_ids = [a["truck_id"] for a in assignments]
        load_ids = [a["load_id"] for a in assignments]
        assert len(truck_ids) == len(set(truck_ids))
        assert len(load_ids) == len(set(load_ids))


def test_aggregate_empty():
    result = _aggregate([])
    assert result["trucks_assigned"] == 0
    assert result["total_distance_km"] == 0
    assert result["total_profit_inr"] == 0


def test_aggregate_sums_and_averages():
    cands = [
        {"distance_km": 100, "cost": 1000, "revenue": 2000, "profit": 1000, "co2_kg": 50,  "route_efficiency_score": 80, "match_score": 150},
        {"distance_km": 200, "cost": 2000, "revenue": 4000, "profit": 2000, "co2_kg": 100, "route_efficiency_score": 60, "match_score": 130},
    ]
    result = _aggregate(cands)
    assert result["trucks_assigned"] == 2
    assert result["total_distance_km"] == 300
    assert result["total_cost_inr"] == 3000
    assert result["total_profit_inr"] == 3000
    assert result["total_co2_kg"] == 150
    assert result["avg_route_efficiency"] == 70.0
    assert result["avg_match_score"] == 140.0


def test_scoring_direction():
    c = {
        "distance_km": 100,
        "revenue": 5000,
        "match_score": 120,
        "profit": 2000,
        "co2_kg": 100,
        "ml_adjustment": 5,
    }
    assert _score("nearest", c) < 0
    assert _score("greedy_profit", c) == 5000
    assert _score("ortools_rules", c) == 120
    # ai = (2000 - 8*100) + 5*300 = 1200 + 1500 = 2700
    assert _score("ai", c) == 2700
