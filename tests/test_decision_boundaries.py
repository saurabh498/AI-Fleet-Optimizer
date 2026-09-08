from unittest.mock import patch

from backend.services.assignment_decision import (
    generate_assignment_decision
)


def matched_test(
    decision_score,
    route_efficiency,
    profit,
    demand=15,
    waiting=2
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
print("PHASE 7.7.3 - BOUNDARY & THRESHOLD AUDIT")
print("=" * 60)


# -------------------------------------------------
# CASE 1: Score exactly 140
# -------------------------------------------------

result1 = matched_test(
    decision_score=140,
    route_efficiency=70,
    profit=10000
)

print("\nCASE 1 - SCORE EXACTLY 140")
print("Expected: ASSIGN_NOW")
print("Actual:", result1["decision"])

assert result1["decision"] == "ASSIGN_NOW"


# -------------------------------------------------
# CASE 2: Score just below 140
# -------------------------------------------------

result2 = matched_test(
    decision_score=139.99,
    route_efficiency=70,
    profit=10000
)

print("\nCASE 2 - SCORE 139.99")
print("Expected: REVIEW")
print("Actual:", result2["decision"])

assert result2["decision"] == "REVIEW"


# -------------------------------------------------
# CASE 3: Efficiency exactly 70
# -------------------------------------------------

result3 = matched_test(
    decision_score=140,
    route_efficiency=70,
    profit=10000
)

print("\nCASE 3 - EFFICIENCY EXACTLY 70")
print("Expected: ASSIGN_NOW")
print("Actual:", result3["decision"])

assert result3["decision"] == "ASSIGN_NOW"


# -------------------------------------------------
# CASE 4: Efficiency just below 70
# -------------------------------------------------

result4 = matched_test(
    decision_score=140,
    route_efficiency=69.99,
    profit=10000
)

print("\nCASE 4 - EFFICIENCY 69.99")
print("Expected: REVIEW")
print("Actual:", result4["decision"])

assert result4["decision"] == "REVIEW"


# -------------------------------------------------
# CASE 5: Profit exactly zero
# -------------------------------------------------

result5 = matched_test(
    decision_score=150,
    route_efficiency=80,
    profit=0
)

print("\nCASE 5 - PROFIT EXACTLY 0")
print("Expected: WAIT")
print("Actual:", result5["decision"])

assert result5["decision"] == "WAIT"


# -------------------------------------------------
# CASE 6: Profit just above zero
# -------------------------------------------------

result6 = matched_test(
    decision_score=140,
    route_efficiency=70,
    profit=0.01
)

print("\nCASE 6 - PROFIT 0.01")
print("Expected: ASSIGN_NOW")
print("Actual:", result6["decision"])

assert result6["decision"] == "ASSIGN_NOW"


# -------------------------------------------------
# NO-MATCH TESTS
# -------------------------------------------------

fake_no_match = {
    "best_match": None,
    "waiting_recommendation": {
        "recommended_waiting_time_hours": 2
    }
}


def no_match_test(demand, waiting):
    fake_context = {
        "truck_id": 2,
        "available": True,
        "city": "Mumbai",
        "predicted_demand": demand,
        "predicted_waiting_time": waiting
    }

    with patch(
        "backend.services.assignment_decision.select_best_backhaul",
        return_value=fake_no_match
    ), patch(
        "backend.services.assignment_decision.build_ml_decision_context",
        return_value=fake_context
    ):
        return generate_assignment_decision(2, None)


# -------------------------------------------------
# CASE 7: Waiting exactly 2 hours
# -------------------------------------------------

result7 = no_match_test(
    demand=15,
    waiting=2
)

print("\nCASE 7 - WAITING EXACTLY 2 HOURS")
print("Expected: WAIT")
print("Actual:", result7["decision"])

assert result7["decision"] == "WAIT"


# -------------------------------------------------
# CASE 8: Waiting 2.01 + demand 20
# -------------------------------------------------

result8 = no_match_test(
    demand=20,
    waiting=2.01
)

print("\nCASE 8 - WAITING 2.01 / DEMAND 20")
print("Expected: REPOSITION")
print("Actual:", result8["decision"])

assert result8["decision"] == "REPOSITION"


# -------------------------------------------------
# CASE 9: Waiting exactly 5 hours
# -------------------------------------------------

result9 = no_match_test(
    demand=15,
    waiting=5
)

print("\nCASE 9 - WAITING EXACTLY 5 HOURS")
print("Expected: WAIT")
print("Actual:", result9["decision"])

assert result9["decision"] == "WAIT"


# -------------------------------------------------
# CASE 10: Waiting 5.01 + low demand
# -------------------------------------------------

result10 = no_match_test(
    demand=15,
    waiting=5.01
)

print("\nCASE 10 - WAITING 5.01 / LOW DEMAND")
print("Expected: RETURN_EMPTY")
print("Actual:", result10["decision"])

assert result10["decision"] == "RETURN_EMPTY"


print("\n" + "=" * 60)
print("7.7.3 BOUNDARY & THRESHOLD AUDIT: PASS")
print("=" * 60)