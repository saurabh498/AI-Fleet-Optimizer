from backend.services.assignment_decision import determine_no_match_action


tests = [
    {
        "name": "SHORT WAIT",
        "demand": 15.0,
        "waiting": 2.0,
        "expected": "WAIT"
    },
    {
        "name": "REPOSITION",
        "demand": 25.0,
        "waiting": 4.0,
        "expected": "REPOSITION"
    },
    {
        "name": "RETURN EMPTY",
        "demand": 8.0,
        "waiting": 6.0,
        "expected": "RETURN_EMPTY"
    }
]


print("=" * 60)
print("PHASE 7.6 - NO-MATCH DECISION CLASSIFICATION")
print("=" * 60)

for test in tests:

    result = determine_no_match_action(
        predicted_demand=test["demand"],
        predicted_waiting_time=test["waiting"]
    )

    print("\nCASE:", test["name"])
    print("Demand:", test["demand"])
    print("Waiting:", test["waiting"])
    print("Decision:", result["decision"])
    print("Action:", result["action"])

    assert result["decision"] == test["expected"]


print("\n7.6.2 NO-MATCH ACTION CLASSIFICATION: PASS")