from unittest.mock import patch

from backend.services.assignment_decision import (
    generate_assignment_decision
)


def run_matched_case(
    decision_score,
    route_efficiency,
    profit,
    demand,
    waiting
):
    fake_backhaul = {
        "best_match": {
            "load_id": 17,
            "match_score": 195,
            "decision_score": decision_score,
            "route_efficiency_score": route_efficiency,
            "estimated_route_profit": profit
        }
    }

    fake_ml_context = {
        "truck_id": 2,
        "available": True,
        "city": "Mumbai",
        "predicted_demand": demand,
        "predicted_waiting_time": waiting
    }

    with patch(
        "backend.services.assignment_decision.select_best_backhaul",
        return_value=fake_backhaul
    ), patch(
        "backend.services.assignment_decision.build_ml_decision_context",
        return_value=fake_ml_context
    ):
        return generate_assignment_decision(2, None)


def test_case_1_strong_shipment():
    result = run_matched_case(
        decision_score=135,
        route_efficiency=90,
        profit=25000,
        demand=35,
        waiting=1.5
    )

    assert result["decision"] == "ASSIGN_NOW"


def test_case_2_moderate_shipment():
    result = run_matched_case(
        decision_score=120,
        route_efficiency=70,
        profit=15000,
        demand=15,
        waiting=2
    )

    assert result["decision"] == "REVIEW"


def test_case_3_poor_route():
    result = run_matched_case(
        decision_score=80,
        route_efficiency=30,
        profit=5000,
        demand=15,
        waiting=2
    )

    assert result["decision"] == "WAIT"


def test_case_4_high_demand_long_wait():
    fake_no_match = {
        "best_match": None,
        "waiting_recommendation": {
            "recommended_waiting_time_hours": 4
        }
    }

    fake_high_demand_context = {
        "truck_id": 2,
        "available": True,
        "city": "Mumbai",
        "predicted_demand": 25,
        "predicted_waiting_time": 4
    }

    with patch(
        "backend.services.assignment_decision.select_best_backhaul",
        return_value=fake_no_match
    ), patch(
        "backend.services.assignment_decision.build_ml_decision_context",
        return_value=fake_high_demand_context
    ):
        result = generate_assignment_decision(2, None)

    assert result["decision"] == "REPOSITION"


def test_case_5_low_demand_very_long_wait():
    fake_no_match = {
        "best_match": None,
        "waiting_recommendation": {
            "recommended_waiting_time_hours": 6
        }
    }

    fake_low_demand_context = {
        "truck_id": 2,
        "available": True,
        "city": "Mumbai",
        "predicted_demand": 8,
        "predicted_waiting_time": 6
    }

    with patch(
        "backend.services.assignment_decision.select_best_backhaul",
        return_value=fake_no_match
    ), patch(
        "backend.services.assignment_decision.build_ml_decision_context",
        return_value=fake_low_demand_context
    ):
        result = generate_assignment_decision(2, None)

    assert result["decision"] == "RETURN_EMPTY"