from backend.models.truck import Truck
from backend.models.shipment import Shipment

from backend.services.backhaul_matching import find_backhaul_matches
from backend.services.fleet_constraints import validate_fleet_candidate
from backend.services.ortools_optimizer import optimize_assignments
from backend.services.route_optimizer import calculate_route_distances

from backend.services.ml_decision_context import (
    build_ml_decision_context
)

from backend.services.assignment_decision import (
    calculate_ml_adjustment
)


def optimize_fleet(db):
    """
    Generate globally optimized fleet-level
    truck-load recommendations.

    Hard constraints are validated before
    a truck-load pair becomes a candidate.

    ML demand and waiting-time predictions
    are used to adjust the decision score
    before global OR-Tools optimization.
    """

    # -------------------------------------------------
    # Get available trucks
    # -------------------------------------------------

    trucks = db.query(Truck).filter(
        Truck.status == "available"
    ).all()

    # -------------------------------------------------
    # Get available shipments
    # -------------------------------------------------

    shipments = db.query(Shipment).filter(
        Shipment.status == "available"
    ).all()

    # -------------------------------------------------
    # No available trucks
    # -------------------------------------------------

    if not trucks:
        return {
            "message": "No available trucks found",
            "assignments": []
        }

    # -------------------------------------------------
    # No available shipments
    # -------------------------------------------------

    if not shipments:
        return {
            "message": "No available shipments found",
            "assignments": []
        }

    all_candidates = []
    rejected_candidates = 0

    # -------------------------------------------------
    # Generate candidates for every available truck
    # -------------------------------------------------

    for truck in trucks:

        # -------------------------------------------------
        # Validate truck location
        # -------------------------------------------------

        truck_has_valid_location = (
            truck.current_latitude is not None
            and truck.current_longitude is not None
        )

        if not truck_has_valid_location:
            continue

        # -------------------------------------------------
        # Find backhaul matches
        # -------------------------------------------------

        result = find_backhaul_matches(
            truck.truck_id,
            db
        )

        if result is None:
            continue

        matches = result.get(
            "matches",
            []
        )

        # -------------------------------------------------
        # Validate every truck-load candidate
        # -------------------------------------------------

        for match in matches:

            load_id = match["load_id"]

            shipment = db.query(Shipment).filter(
                Shipment.load_id == load_id
            ).first()

            if shipment is None:
                rejected_candidates += 1
                continue

            # -------------------------------------------------
            # Hard constraint validation
            # -------------------------------------------------

            validation = validate_fleet_candidate(
                db,
                truck,
                shipment
            )

            if not validation["feasible"]:
                rejected_candidates += 1
                continue

            # -------------------------------------------------
            # Existing decision score
            # -------------------------------------------------

            decision_score = match.get(
                "decision_score",
                match.get(
                    "match_score",
                    0
                )
            )

            # -------------------------------------------------
            # ML Decision Context
            # -------------------------------------------------

            ml_context = build_ml_decision_context(
                truck.truck_id,
                db
            )

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

            ml_adjusted_decision_score = round(
                float(decision_score)
                + float(ml_adjustment),
                2
            )

            # -------------------------------------------------
            # Route calculation
            # -------------------------------------------------

            route_distances = calculate_route_distances(
                truck.current_latitude,
                truck.current_longitude,
                shipment.pickup_latitude,
                shipment.pickup_longitude,
                shipment.destination_latitude,
                shipment.destination_longitude,
                truck.cost_per_km
            )

            estimated_distance = route_distances[
                "total_distance_km"
            ]

            # -------------------------------------------------
            # Candidate creation
            # -------------------------------------------------

            all_candidates.append({

                "truck_id": truck.truck_id,

                "load_id": match["load_id"],

                "pickup_city": match[
                    "pickup_city"
                ],

                "destination_city": match[
                    "destination_city"
                ],

                "weight": match[
                    "weight"
                ],

                # Existing matching score
                "match_score": match.get(
                    "match_score",
                    0
                ),

                # Original decision score
                "decision_score": decision_score,

                # ML information
                "ml_adjustment": ml_adjustment,

                "ml_adjusted_decision_score": (
                    ml_adjusted_decision_score
                ),

                "predicted_demand": predicted_demand,

                "predicted_waiting_time": (
                    predicted_waiting_time
                ),

                # Route information
                "route_efficiency_score": match.get(
                    "route_efficiency_score",
                    0
                ),

                "estimated_distance": (
                    estimated_distance
                ),

                "estimated_route_cost": match.get(
                    "estimated_route_cost",
                    0
                ),

                "estimated_route_profit": match.get(
                    "estimated_route_profit",
                    match.get(
                        "estimated_net_revenue",
                        0
                    )
                ),

                "recommendation": match.get(
                    "recommendation",
                    "Review"
                ),

                "explanation": (
                    f"Truck #{truck.truck_id} matched with "
                    f"Load #{match['load_id']} because of "
                    f"an ML-adjusted decision score of "
                    f"{ml_adjusted_decision_score}, "
                    f"predicted demand of "
                    f"{predicted_demand:.2f} loads, "
                    f"predicted waiting time of "
                    f"{predicted_waiting_time:.2f} hours, "
                    f"route efficiency of "
                    f"{match.get('route_efficiency_score', 0)}%, "
                    f"and estimated profit of "
                    f"₹{match.get('estimated_route_profit', 0):,.2f}."
                ),
            })

    # -------------------------------------------------
    # No feasible candidates
    # -------------------------------------------------

    if not all_candidates:

        return {
            "message": (
                "No feasible truck-load "
                "combinations found"
            ),

            "total_available_trucks": len(
                trucks
            ),

            "total_available_shipments": len(
                shipments
            ),

            "total_feasible_candidates": 0,

            "rejected_candidates": (
                rejected_candidates
            ),

            "recommended_assignments": 0,

            "assignments": []
        }

    # -------------------------------------------------
    # Global ranking
    #
    # ML-adjusted score is now the primary
    # decision ranking factor.
    # -------------------------------------------------

    all_candidates.sort(
        key=lambda item: (
            item[
                "ml_adjusted_decision_score"
            ],

            item[
                "route_efficiency_score"
            ],

            item[
                "estimated_route_profit"
            ]
        ),

        reverse=True
    )

    # -------------------------------------------------
    # OR-Tools fleet-level optimization
    # -------------------------------------------------

    selected_assignments = optimize_assignments(
        all_candidates
    )

    # -------------------------------------------------
    # Final response
    # -------------------------------------------------

    return {

        "message": (
            "Fleet optimization recommendations "
            "generated successfully"
        ),

        "total_available_trucks": len(
            trucks
        ),

        "total_available_shipments": len(
            shipments
        ),

        "total_feasible_candidates": len(
            all_candidates
        ),

        "rejected_candidates": (
            rejected_candidates
        ),

        "recommended_assignments": len(
            selected_assignments
        ),

        "assignments": selected_assignments
    }