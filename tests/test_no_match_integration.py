from unittest.mock import patch

from backend.services.assignment_decision import (
    generate_assignment_decision
)


def run_test(demand, waiting):
    fake_backhaul = {
        "best_match": None,
        "waiting_recommendation": {
            "recommended_waiting_time_hours": 1,
            "reason": "Controlled test",
            "action": "Test action",
            "priority": "Test"
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
        result = generate_assignment_decision(2, None)

    print("\n" + "-" * 60)
    print(f"Demand: {demand}")
    print(f"Waiting: {waiting}")
    print(f"Decision: {result['decision']}")
    print(f"Action: {result['action']}")
    print(f"ML Decision: {result['ml_decision']}")
    print(f"ML Impact: {result['ml_explanation']['impact']}")

    return result


print("=" * 60)
print("PHASE 7.6.3 - DECISION ENGINE INTEGRATION TEST")
print("=" * 60)

# Case 1: Short wait
result1 = run_test(15, 2)

# Case 2: High demand but long wait
result2 = run_test(25, 4)

# Case 3: Low demand and very long wait
result3 = run_test(8, 6)

assert result1["decision"] == "WAIT"
assert result2["decision"] == "REPOSITION"
assert result3["decision"] == "RETURN_EMPTY"

assert result1["ml_decision"] == "WAIT_FOR_DEMAND"
assert result2["ml_decision"] == "REPOSITION_FOR_DEMAND"
assert result3["ml_decision"] == "RETURN_EMPTY"

assert result1["ml_explanation"]["impact"] == "NEUTRAL"
assert result2["ml_explanation"]["impact"] == "POSITIVE"
assert result3["ml_explanation"]["impact"] == "NEGATIVE"

print("\n" + "=" * 60)
print("7.6.3 DECISION ENGINE INTEGRATION: PASS")
print("=" * 60)