from backend.services.best_backhaul import select_best_backhaul


def generate_assignment_decision(
    truck_id: int,
    db
):
    """
    Generate an intelligent assignment decision
    for the best available backhaul shipment.

    Possible decisions:
    - ASSIGN_NOW
    - REVIEW
    - WAIT
    """

    result = select_best_backhaul(
        truck_id,
        db
    )

    if result is None:
        return None

    best_match = result.get("best_match")

    # -------------------------------------------------
    # Case 1: No suitable shipment
    # -------------------------------------------------

    if best_match is None:

        return {
            "truck_id": truck_id,
            "decision": "WAIT",
            "action": "Wait for a better backhaul shipment",
            "reason": (
                "No suitable backhaul shipment is currently "
                "available"
            ),
            "best_match": None,
            "waiting_recommendation": result.get(
                "waiting_recommendation"
            )
        }

    # -------------------------------------------------
    # Get decision metrics
    # -------------------------------------------------

    decision_score = best_match.get(
        "decision_score",
        0
    )

    route_efficiency = best_match.get(
        "route_efficiency_score",
        0
    )

    estimated_profit = best_match.get(
        "estimated_route_profit",
        0
    )

    # -------------------------------------------------
    # Decision rules
    # -------------------------------------------------

    if (
        decision_score >= 140
        and route_efficiency >= 70
        and estimated_profit > 0
    ):

        decision = "ASSIGN_NOW"

        action = (
            "Assign this shipment to the truck"
        )

        reason = (
            "The shipment has a strong overall decision "
            "score, excellent route efficiency and "
            "positive estimated profit."
        )

    elif (
        decision_score >= 100
        and route_efficiency >= 40
        and estimated_profit > 0
    ):

        decision = "REVIEW"

        action = (
            "Review the shipment before assignment"
        )

        reason = (
            "The shipment is financially viable but "
            "requires additional review before assignment."
        )

    else:

        decision = "WAIT"

        action = (
            "Wait for a better backhaul opportunity"
        )

        reason = (
            "The current shipment does not provide a "
            "strong enough overall route and profitability "
            "score."
        )

    return {
        "truck_id": truck_id,

        "decision": decision,

        "action": action,

        "reason": reason,

        "best_match": best_match,

        "decision_metrics": {
            "decision_score": decision_score,
            "route_efficiency_score": route_efficiency,
            "estimated_route_profit": estimated_profit
        }
    }