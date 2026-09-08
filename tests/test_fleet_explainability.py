from backend.services.ortools_optimizer import optimize_assignments


candidate = {
    "truck_id": 2,
    "load_id": 17,
    "pickup_city": "Mumbai",
    "destination_city": "Pune",
    "weight": 3000,
    "match_score": 195,
    "decision_score": 195,
    "ml_adjustment": 0,
    "ml_adjusted_decision_score": 195,
    "predicted_demand": 17.5,
    "predicted_waiting_time": 2.05,
    "route_efficiency_score": 89.27,
    "estimated_distance": 120.15,
    "estimated_route_cost": 3003.75,
    "estimated_route_profit": 24996.25,
    "recommendation": "Highly Recommended",
    "explanation": (
        "Truck #2 matched with Load #17 because of "
        "an ML-adjusted decision score of 195, "
        "predicted demand of 17.50 loads, "
        "predicted waiting time of 2.05 hours, "
        "route efficiency of 89.27%, "
        "and estimated profit of ₹24,996.25."
    )
}


result = optimize_assignments([candidate])

print("FLEET EXPLANATION:")
print(result[0]["explanation"])

print("\nML DATA:")
print({
    "ml_adjustment": result[0]["ml_adjustment"],
    "ml_adjusted_decision_score": result[0][
        "ml_adjusted_decision_score"
    ],
    "predicted_demand": result[0]["predicted_demand"],
    "predicted_waiting_time": result[0][
        "predicted_waiting_time"
    ]
})

print("\nOPTIMIZATION:")
print({
    "optimization_score": result[0][
        "optimization_score"
    ],
    "optimization_basis": result[0][
        "optimization_basis"
    ]
})