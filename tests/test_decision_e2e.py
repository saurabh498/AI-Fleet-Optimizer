from backend.database.connection import SessionLocal
from backend.models.truck import Truck

from backend.services.backhaul_matching import find_backhaul_matches
from backend.services.ml_decision_context import build_ml_decision_context
from backend.services.assignment_decision import generate_assignment_decision


print("=" * 70)
print("PHASE 7.7.4 - END-TO-END DECISION ENGINE AUDIT")
print("=" * 70)

db = SessionLocal()

try:
    # -------------------------------------------------
    # Find any truck for controlled temporary testing
    # -------------------------------------------------

    truck = (
        db.query(Truck)
        .order_by(Truck.truck_id)
        .first()
    )

    if truck is None:
        raise AssertionError("No trucks found in database")

    truck_id = truck.truck_id

    print("\nORIGINAL TRUCK STATE")
    print({
        "truck_id": truck.truck_id,
        "status": truck.status,
        "city": truck.current_city,
        "current_load": truck.current_load,
        "destination": truck.destination
    })

    # -------------------------------------------------
    # Temporarily make truck available
    # -------------------------------------------------

    original_status = truck.status
    original_load = truck.current_load
    original_destination = truck.destination

    truck.status = "available"
    truck.current_load = 0
    truck.destination = None

    db.flush()

    print("\nTEMPORARY TEST STATE")
    print({
        "truck_id": truck.truck_id,
        "status": truck.status,
        "city": truck.current_city,
        "current_load": truck.current_load,
        "destination": truck.destination
    })

    # -------------------------------------------------
    # 1. Backhaul Matching
    # -------------------------------------------------

    matching = find_backhaul_matches(
        truck_id,
        db
    )

    assert matching is not None

    matches = matching.get("matches", [])

    print("\n1. BACKHAUL MATCHING")
    print({
        "total_matches": len(matches),
        "waiting_recommendation":
            matching.get("waiting_recommendation")
    })

    # -------------------------------------------------
    # 2. ML Decision Context
    # -------------------------------------------------

    ml_context = build_ml_decision_context(
        truck_id,
        db
    )

    assert ml_context is not None
    assert ml_context.get("available") is True

    print("\n2. ML DECISION CONTEXT")
    print({
        "predicted_demand":
            ml_context.get("predicted_demand"),
        "predicted_waiting_time":
            ml_context.get("predicted_waiting_time"),
        "demand_model":
            ml_context.get("demand_model"),
        "demand_model_version":
            ml_context.get("demand_model_version"),
        "waiting_model":
            ml_context.get("waiting_model"),
        "waiting_model_version":
            ml_context.get("waiting_model_version")
    })

    # -------------------------------------------------
    # 3. Final Decision Engine
    # -------------------------------------------------

    decision = generate_assignment_decision(
        truck_id,
        db
    )

    assert decision is not None

    print("\n3. FINAL DECISION")
    print({
        "decision": decision.get("decision"),
        "action": decision.get("action"),
        "reason": decision.get("reason")
    })

    # -------------------------------------------------
    # 4. Decision Validation
    # -------------------------------------------------

    valid_decisions = {
        "ASSIGN_NOW",
        "REVIEW",
        "WAIT",
        "REPOSITION",
        "RETURN_EMPTY"
    }

    assert decision.get("decision") in valid_decisions

    # -------------------------------------------------
    # 5. ML Integration Validation
    # -------------------------------------------------

    assert decision.get("ml_context") is not None
    assert decision.get("ml_explanation") is not None

    explanation = decision["ml_explanation"]

    assert "impact" in explanation
    assert "ml_adjustment" in explanation
    assert "base_score" in explanation
    assert "ml_adjusted_score" in explanation
    assert "reason" in explanation

    print("\n4. ML EXPLANATION")
    print(explanation)

    # -------------------------------------------------
    # 6. Matched / No-Match Validation
    # -------------------------------------------------

    if decision.get("best_match") is not None:

        best_match = decision["best_match"]

        required_fields = [
            "load_id",
            "decision_score",
            "route_efficiency_score",
            "estimated_route_profit"
        ]

        for field in required_fields:
            assert field in best_match

        metrics = decision.get(
            "decision_metrics",
            {}
        )

        assert "ml_adjustment" in metrics
        assert "ml_adjusted_score" in metrics
        assert "predicted_demand" in metrics
        assert "predicted_waiting_time" in metrics

        print("\n5. MATCHED SHIPMENT")
        print({
            "load_id": best_match.get("load_id"),
            "decision_score":
                best_match.get("decision_score"),
            "route_efficiency":
                best_match.get(
                    "route_efficiency_score"
                ),
            "estimated_profit":
                best_match.get(
                    "estimated_route_profit"
                ),
            "ml_adjustment":
                metrics.get("ml_adjustment"),
            "ml_adjusted_score":
                metrics.get(
                    "ml_adjusted_score"
                )
        })

    else:

        assert decision.get("decision") in {
            "WAIT",
            "REPOSITION",
            "RETURN_EMPTY"
        }

        print("\n5. NO-MATCH OPERATIONAL DECISION")
        print({
            "decision":
                decision.get("decision"),
            "ml_decision":
                decision.get("ml_decision")
        })

    # -------------------------------------------------
    # Restore original in-memory state
    # -------------------------------------------------

    truck.status = original_status
    truck.current_load = original_load
    truck.destination = original_destination

    db.rollback()

    print("\n6. DATABASE STATE")
    print("Temporary changes rolled back: YES")

    print("\n" + "=" * 70)
    print("7.7.4 END-TO-END DECISION ENGINE AUDIT: PASS")
    print("=" * 70)

finally:
    db.close()