from backend.services.assignment_decision import (
    calculate_ml_adjustment,
    generate_ml_explanation
)


BASE_SCORE = 134.28


tests = [
    {
        "name": "POSITIVE ML IMPACT",
        "demand": 35,
        "waiting": 1.5
    },
    {
        "name": "NEGATIVE ML IMPACT",
        "demand": 8,
        "waiting": 6.0
    },
    {
        "name": "NEUTRAL ML IMPACT",
        "demand": 15,
        "waiting": 2.0
    }
]


for test in tests:

    demand = test["demand"]
    waiting = test["waiting"]

    adjustment = calculate_ml_adjustment(
        predicted_demand=demand,
        predicted_waiting_time=waiting
    )

    adjusted_score = round(
        BASE_SCORE + adjustment,
        2
    )

    explanation = generate_ml_explanation(
        predicted_demand=demand,
        predicted_waiting_time=waiting,
        ml_adjustment=adjustment,
        base_score=BASE_SCORE,
        ml_adjusted_score=adjusted_score
    )

    print("\n" + "=" * 60)
    print(test["name"])
    print("=" * 60)

    print({
        "predicted_demand": demand,
        "predicted_waiting_time": waiting,
        "ml_adjustment": adjustment,
        "base_score": BASE_SCORE,
        "ml_adjusted_score": adjusted_score,
        "impact": explanation["impact"],
        "reason": explanation["reason"]
    })