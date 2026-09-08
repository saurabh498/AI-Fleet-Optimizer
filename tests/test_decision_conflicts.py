from unittest.mock import patch

from backend.services.assignment_decision import (
    generate_assignment_decision
)


def matched_test(
    decision_score,
    route_efficiency,
    profit,
    demand,
    waiting
):
    fake_backhaul = {
        "best_match": {
            "load_id": 17,
            "match_score": decision_score,
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
print("PHASE 7.7.2 - CONFLICT RESOLUTION AUDIT")
print("=" * 60)


# -------------------------------------------------
# CASE 1
# High score but poor route efficiency
# Route efficiency must block ASSIGN_NOW
# -------------------------------------------------

result1 = matched_test(
    decision_score=160,
    route_efficiency=30,
    profit=25000,
    demand=35,
    waiting=1.5
)

print("\nCASE 1 - HIGH SCORE / POOR ROUTE")
print("Expected: WAIT")
print("Actual:", result1["decision"])
print(
    "ML Adjusted Score:",
    result1["decision_metrics"]["ml_adjusted_score"]
)

assert result1["decision"] == "WAIT"


# -------------------------------------------------
# CASE 2
# High score and good route but zero profit
# Profit constraint must block assignment
# -------------------------------------------------

result2 = matched_test(
    decision_score=180,
    route_efficiency=90,
    profit=0,
    demand=35,
    waiting=1.5
)

print("\nCASE 2 - HIGH SCORE / ZERO PROFIT")
print("Expected: WAIT")
print("Actual:", result2["decision"])
print(
    "ML Adjusted Score:",
    result2["decision_metrics"]["ml_adjusted_score"]
)

assert result2["decision"] == "WAIT"


# -------------------------------------------------
# CASE 3
# ML positive adjustment crosses ASSIGN_NOW threshold
# 135 + 10 = 145
# -------------------------------------------------

result3 = matched_test(
    decision_score=135,
    route_efficiency=90,
    profit=25000,
    demand=35,
    waiting=1.5
)

print("\nCASE 3 - ML POSITIVE THRESHOLD CROSSING")
print("Base Score: 135")
print("ML Adjustment: +10")
print("Expected: ASSIGN_NOW")
print("Actual:", result3["decision"])
print(
    "ML Adjusted Score:",
    result3["decision_metrics"]["ml_adjusted_score"]
)

assert result3["decision"] == "ASSIGN_NOW"
assert result3["decision_metrics"]["ml_adjusted_score"] == 145


# -------------------------------------------------
# CASE 4
# ML negative adjustment pushes score below
# ASSIGN_NOW threshold
# 145 - 10 = 135
# -------------------------------------------------

result4 = matched_test(
    decision_score=145,
    route_efficiency=90,
    profit=25000,
    demand=8,
    waiting=6
)

print("\nCASE 4 - ML NEGATIVE THRESHOLD CROSSING")
print("Base Score: 145")
print("ML Adjustment: -10")
print("Expected: REVIEW")
print("Actual:", result4["decision"])
print(
    "ML Adjusted Score:",
    result4["decision_metrics"]["ml_adjusted_score"]
)

assert result4["decision"] == "REVIEW"
assert result4["decision_metrics"]["ml_adjusted_score"] == 135


# -------------------------------------------------
# CASE 5
# No shipment + high demand + long waiting
# Operational decision should be REPOSITION
# -------------------------------------------------

fake_no_match = {
    "best_match": None,
    "waiting_recommendation": {
        "recommended_waiting_time_hours": 4,
        "reason": "No suitable shipment",
        "action": "Recheck",
        "priority": "Medium"
    }
}

fake_context = {
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
    return_value=fake_context
):
    result5 = generate_assignment_decision(2, None)

print("\nCASE 5 - HIGH DEMAND / LONG WAIT / NO SHIPMENT")
print("Expected: REPOSITION")
print("Actual:", result5["decision"])
print("ML Decision:", result5["ml_decision"])

assert result5["decision"] == "REPOSITION"
assert result5["ml_decision"] == "REPOSITION_FOR_DEMAND"


print("\n" + "=" * 60)
print("7.7.2 CONFLICT RESOLUTION AUDIT: PASS")
print("=" * 60)