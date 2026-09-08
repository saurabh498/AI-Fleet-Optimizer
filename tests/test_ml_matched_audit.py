from backend.services.assignment_decision import (
    calculate_ml_adjustment,
    generate_ml_explanation
)


decision_score = 134.28
predicted_demand = 17.5
predicted_waiting_time = 2.05


ml_adjustment = calculate_ml_adjustment(
    predicted_demand=predicted_demand,
    predicted_waiting_time=predicted_waiting_time
)

ml_adjusted_score = round(
    decision_score + ml_adjustment,
    2
)

explanation = generate_ml_explanation(
    predicted_demand=predicted_demand,
    predicted_waiting_time=predicted_waiting_time,
    ml_adjustment=ml_adjustment,
    base_score=decision_score,
    ml_adjusted_score=ml_adjusted_score
)


print("MATCHED ML DECISION AUDIT")
print("=" * 50)

print({
    "decision_score": decision_score,
    "predicted_demand": predicted_demand,
    "predicted_waiting_time": predicted_waiting_time,
    "ml_adjustment": ml_adjustment,
    "ml_adjusted_score": ml_adjusted_score
})

print("\nML EXPLANATION:")
print(explanation)