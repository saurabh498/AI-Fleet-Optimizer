from unittest.mock import patch

from backend.services.assignment_decision import generate_assignment_decision


mock_backhaul_result = {
    "truck_id": 2,
    "best_match": {
        "load_id": 17,
        "match_score": 120,
        "decision_score": 80.0,
        "route_efficiency_score": 30.0,
        "estimated_route_profit": 5000.0
    },
    "waiting_recommendation": {
        "recommended_waiting_time_hours": 2,
        "reason": "Weak current backhaul opportunity",
        "action": "Wait for a better shipment"
    }
}


mock_ml_context = {
    "truck_id": 2,
    "available": True,
    "city": "Mumbai",
    "predicted_demand": 15.0,
    "predicted_waiting_time": 2.0,
    "demand_model": "XGBoost Regressor",
    "demand_model_version": "xgboost-v1",
    "waiting_model": "Linear Regression",
    "waiting_model_version": "baseline-waiting-v1"
}


with patch(
    "backend.services.assignment_decision.select_best_backhaul",
    return_value=mock_backhaul_result
), patch(
    "backend.services.assignment_decision.build_ml_decision_context",
    return_value=mock_ml_context
):

    result = generate_assignment_decision(
        truck_id=2,
        db=None
    )


print("=" * 60)
print("PHASE 7.5 - WAIT DECISION VALIDATION")
print("=" * 60)

print("\nDecision:", result["decision"])
print("Action:", result["action"])
print("Reason:", result["reason"])

print("\nDecision Metrics:")
print(result["decision_metrics"])

print("\nML Explanation:")
print(result["ml_explanation"])


assert result["decision"] == "WAIT"
assert result["decision_metrics"]["ml_adjustment"] == 0.0
assert result["decision_metrics"]["ml_adjusted_score"] == 80.0
assert result["best_match"]["route_efficiency_score"] < 40
assert result["best_match"]["estimated_route_profit"] > 0

print("\n7.5 WAIT VALIDATION: PASS")