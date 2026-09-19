from backend.services.best_backhaul import select_best_backhaul
from backend.services.ml_decision_context import build_ml_decision_context


# -------------------------------------------------
# SHAP helper
# -------------------------------------------------

def _shap_from_context(ml_context: dict) -> dict:
    """
    Extract the SHAP explanation from an ML decision
    context. Returns a safe fallback when SHAP is
    unavailable.
    """
    if not ml_context or not ml_context.get("available"):
        return {
            "summary": "SHAP explanation unavailable — no ML context",
            "top_drivers": [],
            "top_negative": [],
        }

    shap_data = ml_context.get("shap_explanation", {})

    return {
        "summary": shap_data.get("summary", "N/A"),
        "predicted_value": shap_data.get("predicted_value"),
        "base_value": shap_data.get("base_value"),
        "top_drivers": shap_data.get("top_positive", [])[:3],
        "top_negative": shap_data.get("top_negative", [])[:3],
    }


def calculate_ml_adjustment(
    predicted_demand: float,
    predicted_waiting_time: float
) -> float:
    """
    Calculate a controlled ML-based adjustment
    for the assignment decision score.

    The adjustment is intentionally limited to
    a small range so that ML does not override
    route efficiency and profitability logic.
    """

    adjustment = 0.0

    # -------------------------------------------------
    # High demand + short waiting time
    # -------------------------------------------------

    if (
        predicted_demand >= 30
        and predicted_waiting_time <= 2
    ):
        adjustment = 10.0

    # -------------------------------------------------
    # Good demand + acceptable waiting time
    # -------------------------------------------------

    elif (
        predicted_demand >= 20
        and predicted_waiting_time <= 3
    ):
        adjustment = 5.0

    # -------------------------------------------------
    # Very low demand
    # -------------------------------------------------

    elif predicted_demand < 10:
        adjustment = -5.0

    # -------------------------------------------------
    # Long waiting time
    # -------------------------------------------------

    if predicted_waiting_time > 5:
        adjustment = -10.0

    elif predicted_waiting_time > 3:
        adjustment = min(
            adjustment,
            -5.0
        )

    return adjustment


def determine_no_match_action(
    predicted_demand: float,
    predicted_waiting_time: float
) -> dict:
    """
    Determine the operational action when no suitable
    backhaul shipment is currently available.

    Possible actions:
    - WAIT
    - REPOSITION
    - RETURN_EMPTY
    """

    # -------------------------------------------------
    # Short waiting time
    # -------------------------------------------------

    if predicted_waiting_time <= 2:
        return {
            "decision": "WAIT",
            "action": "Wait briefly for a possible backhaul shipment",
            "reason": (
                f"Predicted waiting time is only "
                f"{predicted_waiting_time:.2f} hours."
            ),
            "priority": "HIGH"
        }

    # -------------------------------------------------
    # High demand but longer waiting
    # -------------------------------------------------

    if (
        predicted_waiting_time > 2
        and predicted_demand >= 20
    ):
        return {
            "decision": "REPOSITION",
            "action": (
                "Reposition the truck toward a higher-demand "
                "location and search for new backhaul opportunities"
            ),
            "reason": (
                f"Predicted demand is "
                f"{predicted_demand:.2f} loads, but expected "
                f"waiting time is {predicted_waiting_time:.2f} hours. "
                "Repositioning may provide a better opportunity."
            ),
            "priority": "MEDIUM"
        }

    # -------------------------------------------------
    # Long waiting + low demand
    # -------------------------------------------------

    if (
        predicted_waiting_time > 5
        and predicted_demand < 20
    ):
        return {
            "decision": "RETURN_EMPTY",
            "action": (
                "Return empty because waiting for a backhaul "
                "shipment is not economically attractive"
            ),
            "reason": (
                f"Predicted demand is only "
                f"{predicted_demand:.2f} loads and expected "
                f"waiting time is {predicted_waiting_time:.2f} hours."
            ),
            "priority": "LOW"
        }

    # -------------------------------------------------
    # Moderate waiting / uncertain demand
    # -------------------------------------------------

    return {
        "decision": "WAIT",
        "action": "Wait and recheck for a better backhaul opportunity",
        "reason": (
            f"Predicted demand is {predicted_demand:.2f} loads "
            f"with an expected waiting time of "
            f"{predicted_waiting_time:.2f} hours."
        ),
        "priority": "MEDIUM"
    }


def generate_ml_explanation(
    predicted_demand: float,
    predicted_waiting_time: float,
    ml_adjustment: float,
    base_score: float,
    ml_adjusted_score: float
) -> dict:
    """
    Generate a human-readable explanation
    for the ML impact on the assignment decision.
    """

    if ml_adjustment > 0:
        if predicted_demand >= 30 and predicted_waiting_time <= 2:
            reason = (
                f"High predicted demand of {predicted_demand:.2f} loads "
                f"and low predicted waiting time of "
                f"{predicted_waiting_time:.2f} hours."
            )
        else:
            reason = (
                f"Moderate predicted demand of {predicted_demand:.2f} loads "
                f"with an acceptable waiting time of "
                f"{predicted_waiting_time:.2f} hours."
            )

        impact = "POSITIVE"

    elif ml_adjustment < 0:
        if predicted_waiting_time > 5:
            reason = (
                f"Long predicted waiting time of "
                f"{predicted_waiting_time:.2f} hours."
            )
        elif predicted_demand < 10:
            reason = (
                f"Low predicted demand of "
                f"{predicted_demand:.2f} loads."
            )
        else:
            reason = (
                f"Predicted demand of {predicted_demand:.2f} loads "
                f"and waiting time of "
                f"{predicted_waiting_time:.2f} hours."
            )

        impact = "NEGATIVE"

    else:
        reason = (
            f"Predicted demand of {predicted_demand:.2f} loads "
            f"and waiting time of "
            f"{predicted_waiting_time:.2f} hours did not trigger "
            f"an ML score adjustment."
        )

        impact = "NEUTRAL"

    return {
        "impact": impact,
        "ml_adjustment": ml_adjustment,
        "base_score": base_score,
        "ml_adjusted_score": ml_adjusted_score,
        "reason": reason
    }


def generate_assignment_decision(
    truck_id: int,
    db
):
    """
    Generate the final assignment decision for a truck.

    Decision flow:

    1. Find the best backhaul shipment.
    2. Build ML decision context.
    3. Evaluate route, profit and existing decision score.
    4. Apply controlled ML adjustment using:
       - Predicted demand
       - Predicted waiting time
    5. Generate final decision:
       - ASSIGN_NOW
       - REVIEW
       - WAIT
    """

    # -------------------------------------------------
    # Get best backhaul shipment
    # -------------------------------------------------

    result = select_best_backhaul(
        truck_id,
        db
    )

    if result is None:
        return None

    # -------------------------------------------------
    # Build ML decision context
    # -------------------------------------------------

    ml_context = build_ml_decision_context(
        truck_id,
        db
    )

    best_match = result.get(
        "best_match"
    )

    # -------------------------------------------------
    # No suitable backhaul shipment
    # -------------------------------------------------

    if best_match is None:
        predicted_demand = 0.0
        predicted_waiting_time = 0.0

        if ml_context and ml_context.get("available"):
            predicted_demand = ml_context.get(
                "predicted_demand",
                0.0
            )

            predicted_waiting_time = ml_context.get(
                "predicted_waiting_time",
                0.0
            )

        # -------------------------------------------------
        # Determine operational action
        # -------------------------------------------------

        no_match_action = determine_no_match_action(
            predicted_demand=predicted_demand,
            predicted_waiting_time=predicted_waiting_time
        )

        decision = no_match_action["decision"]
        action = no_match_action["action"]
        reason = no_match_action["reason"]

        # -------------------------------------------------
        # ML decision classification
        # -------------------------------------------------

        if decision == "WAIT":
            ml_decision = "WAIT_FOR_DEMAND"
            ml_impact = "NEUTRAL"

            ml_reason = (
                f"Predicted demand of "
                f"{predicted_demand:.2f} loads with an expected "
                f"waiting time of "
                f"{predicted_waiting_time:.2f} hours supports "
                "a temporary wait."
            )

        elif decision == "REPOSITION":
            ml_decision = "REPOSITION_FOR_DEMAND"
            ml_impact = "POSITIVE"

            ml_reason = (
                f"Predicted demand of "
                f"{predicted_demand:.2f} loads is attractive, "
                f"but waiting time of "
                f"{predicted_waiting_time:.2f} hours is too long. "
                "Repositioning may improve backhaul availability."
            )

        else:
            ml_decision = "RETURN_EMPTY"
            ml_impact = "NEGATIVE"

            ml_reason = (
                f"Predicted demand of "
                f"{predicted_demand:.2f} loads is low and expected "
                f"waiting time of "
                f"{predicted_waiting_time:.2f} hours is too long. "
                "Waiting is unlikely to be economically efficient."
            )

        # -------------------------------------------------
        # ML explainability
        # -------------------------------------------------

        ml_explanation = {
            "impact": ml_impact,
            "ml_adjustment": 0.0,
            "base_score": 0.0,
            "ml_adjusted_score": 0.0,
            "reason": ml_reason,
            "shap": _shap_from_context(ml_context),
        }

        # -------------------------------------------------
        # Final no-match response
        # -------------------------------------------------

        return {
            "truck_id": truck_id,
            "decision": decision,
            "action": action,
            "reason": reason,
            "best_match": None,
            "waiting_recommendation": result.get(
                "waiting_recommendation"
            ),
            "ml_decision": ml_decision,
            "ml_explanation": ml_explanation,
            "ml_context": ml_context
        }

    # -------------------------------------------------
    # Existing decision metrics
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
    # Get ML prediction values
    # -------------------------------------------------

    predicted_demand = 0.0
    predicted_waiting_time = 0.0

    if (
        ml_context
        and ml_context.get("available")
    ):
        predicted_demand = ml_context.get(
            "predicted_demand",
            0.0
        )

        predicted_waiting_time = ml_context.get(
            "predicted_waiting_time",
            0.0
        )

    # -------------------------------------------------
    # Calculate ML adjustment
    # -------------------------------------------------

    ml_adjustment = calculate_ml_adjustment(
        predicted_demand=predicted_demand,
        predicted_waiting_time=predicted_waiting_time
    )

    # -------------------------------------------------
    # ML-adjusted decision score
    # -------------------------------------------------

    ml_adjusted_score = round(
        decision_score + ml_adjustment,
        2
    )

    ml_explanation = generate_ml_explanation(
        predicted_demand=predicted_demand,
        predicted_waiting_time=predicted_waiting_time,
        ml_adjustment=ml_adjustment,
        base_score=decision_score,
        ml_adjusted_score=ml_adjusted_score,
    )

    ml_explanation["shap"] = _shap_from_context(ml_context)

    # -------------------------------------------------
    # Final decision
    # -------------------------------------------------

    if (
        ml_adjusted_score >= 140
        and route_efficiency >= 70
        and estimated_profit > 0
    ):

        decision = "ASSIGN_NOW"

        action = (
            "Assign this shipment to the truck"
        )

        reason = (
            "The shipment has a strong overall decision "
            "score, excellent route efficiency and positive "
            "estimated profit."
        )

    elif (
        ml_adjusted_score >= 100
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
            "strong enough overall route and profitability score."
        )

    # -------------------------------------------------
    # Final response
    # -------------------------------------------------

    return {
        "truck_id": truck_id,

        "decision": decision,

        "action": action,

        "reason": reason,

        "best_match": best_match,

        "decision_metrics": {
            "decision_score": decision_score,

            "ml_adjustment": ml_adjustment,

            "ml_adjusted_score": ml_adjusted_score,

            "route_efficiency_score": route_efficiency,

            "estimated_route_profit": estimated_profit,

            "predicted_demand": predicted_demand,

            "predicted_waiting_time": predicted_waiting_time
        },
        "ml_explanation": ml_explanation,
        "ml_context": ml_context
    }
