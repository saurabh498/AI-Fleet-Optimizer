from unittest.mock import patch

from backend.services.assignment_decision import (
    generate_assignment_decision
)


def test_matched_case(
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


print("=" * 60)
print("PHASE 7.7.1 - DECISION PRIORITY RULES AUDIT")
print("=" * 60)


# -------------------------------------------------
# CASE 1: Strong shipment
# -------------------------------------------------

result1 = test_matched_case(
    decision_score=135,
    route_efficiency=90,
    profit=25000,
    demand=35,
    waiting=1.5
)

print("\nCASE 1 - STRONG SHIPMENT")
print("Expected: ASSIGN_NOW")
print("Actual:", result1["decision"])
print("ML Adjusted Score:", result1["decision_metrics"]["ml_adjusted_score"])

assert result1["decision"] == "ASSIGN_NOW"


# -------------------------------------------------
# CASE 2: Financially viable but moderate
# -------------------------------------------------

result2 = test_matched_case(
    decision_score=120,
    route_efficiency=70,
    profit=15000,
    demand=15,
    waiting=2
)

print("\nCASE 2 - MODERATE SHIPMENT")
print("Expected: REVIEW")
print("Actual:", result2["decision"])
print("ML Adjusted Score:", result2["decision_metrics"]["ml_adjusted_score"])

assert result2["decision"] == "REVIEW"


# -------------------------------------------------
# CASE 3: Poor route
# -------------------------------------------------

result3 = test_matched_case(
    decision_score=80,
    route_efficiency=30,
    profit=5000,
    demand=15,
    waiting=2
)

print("\nCASE 3 - POOR ROUTE")
print("Expected: WAIT")
print("Actual:", result3["decision"])
print("ML Adjusted Score:", result3["decision_metrics"]["ml_adjusted_score"])

assert result3["decision"] == "WAIT"


# -------------------------------------------------
# CASE 4: High demand but long waiting
# -------------------------------------------------

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
    result4 = generate_assignment_decision(2, None)

print("\nCASE 4 - HIGH DEMAND / LONG WAIT")
print("Expected: REPOSITION")
print("Actual:", result4["decision"])

assert result4["decision"] == "REPOSITION"


# -------------------------------------------------
# CASE 5: Low demand and very long waiting
# -------------------------------------------------

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
    result5 = generate_assignment_decision(2, None)

print("\nCASE 5 - LOW DEMAND / VERY LONG WAIT")
print("Expected: RETURN_EMPTY")
print("Actual:", result5["decision"])

assert result5["decision"] == "RETURN_EMPTY"


print("\n" + "=" * 60)
print("7.7.1 DECISION PRIORITY RULES AUDIT: PASS")
print("=" * 60)