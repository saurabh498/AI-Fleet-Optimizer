from backend.services.ortools_optimizer import optimize_assignments


def create_candidate(decision_score):
    return {
        "truck_id": 999,
        "load_id": 999,
        "match_score": 195,
        "decision_score": decision_score,
        "ml_adjusted_decision_score": decision_score,
        "route_efficiency_score": 89.27,
        "estimated_route_cost": 3003.75,
        "estimated_route_profit": 24996.25,
    }


without_ml = create_candidate(134.28)
with_ml = create_candidate(144.28)

result_without_ml = optimize_assignments(
    [without_ml]
)

result_with_ml = optimize_assignments(
    [with_ml]
)

print("WITHOUT ML:")
print({
    "decision_score": without_ml["decision_score"],
    "ml_adjusted_score": without_ml[
        "ml_adjusted_decision_score"
    ],
    "optimization_score": result_without_ml[0][
        "optimization_score"
    ]
})

print("\nWITH ML:")
print({
    "decision_score": with_ml["decision_score"],
    "ml_adjusted_score": with_ml[
        "ml_adjusted_decision_score"
    ],
    "optimization_score": result_with_ml[0][
        "optimization_score"
    ]
})

print("\nOPTIMIZATION SCORE IMPACT:")

difference = (
    result_with_ml[0]["optimization_score"]
    - result_without_ml[0]["optimization_score"]
)

print({
    "optimization_score_difference": round(
        difference,
        2
    )
})