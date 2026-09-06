from backend.services.backhaul_matching import find_backhaul_matches


def select_best_backhaul(
    truck_id: int,
    db
):
    """
    Select the best backhaul shipment for a truck.

    Uses existing backhaul matching results and
    applies a final decision score based on:
    - Match score
    - Route efficiency
    - Estimated profit
    """

    result = find_backhaul_matches(
        truck_id,
        db
    )

    if result is None:
        return None

    matches = result.get("matches", [])

    # -------------------------------------------------
    # No suitable matches
    # -------------------------------------------------

    if not matches:
        return {
            "truck_id": truck_id,
            "message": "No suitable backhaul shipment available",
            "best_match": None,
            "waiting_recommendation": result.get(
                "waiting_recommendation"
            )
        }

    best_match = None
    highest_decision_score = float("-inf")

    # -------------------------------------------------
    # Evaluate every candidate
    # -------------------------------------------------

    for match in matches:

        match_score = match.get(
            "match_score",
            0
        )

        efficiency_score = match.get(
            "route_efficiency_score",
            0
        )

        estimated_profit = match.get(
            "estimated_route_profit",
            match.get(
                "estimated_net_revenue",
                0
            )
        )

        # -------------------------------------------------
        # Normalize profit
        # -------------------------------------------------

        profit_score = min(
            max(
                estimated_profit / 500,
                0
            ),
            100
        )

        # -------------------------------------------------
        # Final decision score
        # -------------------------------------------------

        decision_score = round(
            (
                match_score * 0.50
                + efficiency_score * 0.30
                + profit_score * 0.20
            ),
            2
        )

        match["decision_score"] = decision_score

        # -------------------------------------------------
        # Select highest score
        # -------------------------------------------------

        if decision_score > highest_decision_score:

            highest_decision_score = decision_score
            best_match = match

    # -------------------------------------------------
    # Generate explanation
    # -------------------------------------------------

    explanation = (
        f"Load #{best_match['load_id']} selected because "
        f"it has a match score of "
        f"{best_match['match_score']}, "
        f"route efficiency of "
        f"{best_match['route_efficiency_score']}%, "
        f"and estimated route profit of "
        f"₹{best_match['estimated_route_profit']:,.2f}."
    )

    # -------------------------------------------------
    # Final recommendation
    # -------------------------------------------------

    if highest_decision_score >= 150:
        final_recommendation = "Highly Recommended"

    elif highest_decision_score >= 120:
        final_recommendation = "Recommended"

    elif highest_decision_score >= 90:
        final_recommendation = "Moderately Recommended"

    else:
        final_recommendation = "Low Priority"

    return {
        "truck_id": truck_id,

        "message": "Best backhaul shipment selected",

        "best_match": best_match,

        "final_decision_score": highest_decision_score,

        "final_recommendation": final_recommendation,

        "explanation": explanation
    }