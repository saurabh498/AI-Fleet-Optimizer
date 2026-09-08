from backend.models.truck import Truck
from backend.models.shipment import Shipment

from backend.services.baseline_matching import find_baseline_match
from backend.services.best_backhaul import select_best_backhaul
from backend.services.route_optimizer import calculate_route_distances


def evaluate_strategy(
    truck,
    shipment,
    strategy
):
    """
    Calculate common evaluation metrics for a selected shipment.

    This function does not modify the database.
    """

    if shipment is None:
        return None

    if (
        truck.current_latitude is None
        or truck.current_longitude is None
        or shipment.pickup_latitude is None
        or shipment.pickup_longitude is None
        or shipment.destination_latitude is None
        or shipment.destination_longitude is None
    ):
        return {
            "strategy": strategy,
            "load_id": shipment.load_id,
            "pickup_city": shipment.pickup_city,
            "destination_city": shipment.destination_city,
            "revenue": shipment.revenue,
            "metrics_available": False,
            "message": "Complete location data is not available"
        }

    route = calculate_route_distances(
        truck_latitude=truck.current_latitude,
        truck_longitude=truck.current_longitude,
        pickup_latitude=shipment.pickup_latitude,
        pickup_longitude=shipment.pickup_longitude,
        destination_latitude=shipment.destination_latitude,
        destination_longitude=shipment.destination_longitude,
        cost_per_km=truck.cost_per_km
    )

    total_distance = route["total_distance_km"]
    estimated_cost = route["estimated_cost"]
    revenue = shipment.revenue
    estimated_profit = revenue - estimated_cost

    remaining_capacity = truck.capacity - truck.current_load

    utilization = 0

    if remaining_capacity > 0:
        utilization = (
            shipment.weight / remaining_capacity
        ) * 100

    return {
        "strategy": strategy,
        "load_id": shipment.load_id,
        "pickup_city": shipment.pickup_city,
        "destination_city": shipment.destination_city,
        "weight": shipment.weight,
        "revenue": revenue,
        "pickup_distance_km": round(
            route["pickup_distance_km"],
            2
        ),
        "delivery_distance_km": round(
            route["delivery_distance_km"],
            2
        ),
        "total_distance_km": round(
            total_distance,
            2
        ),
        "estimated_cost": round(
            estimated_cost,
            2
        ),
        "estimated_profit": round(
            estimated_profit,
            2
        ),
        "capacity_utilization_percent": round(
            utilization,
            2
        ),
        "metrics_available": True
    }


def compare_baseline_vs_ai(
    truck_id: int,
    db
):
    """
    Controlled Baseline vs AI comparison.

    Both strategies receive the same:
    - truck state
    - current truck location
    - available shipment pool

    No database state is modified.
    """

    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        return {
            "truck_id": truck_id,
            "message": "Truck not found"
        }

    # -------------------------------------------------
    # 1. Run baseline strategy
    # -------------------------------------------------

    baseline_result = find_baseline_match(
        truck_id,
        db
    )

    # -------------------------------------------------
    # 2. Run AI strategy
    # -------------------------------------------------

    ai_result = select_best_backhaul(
        truck_id,
        db
    )

    # -------------------------------------------------
    # 3. Get baseline shipment
    # -------------------------------------------------

    baseline_evaluation = None

    if baseline_result.get("matched"):

        baseline_load_id = baseline_result[
            "selected_load"
        ]["load_id"]

        baseline_shipment = db.query(
            Shipment
        ).filter(
            Shipment.load_id == baseline_load_id
        ).first()

        baseline_evaluation = evaluate_strategy(
            truck,
            baseline_shipment,
            "BASELINE"
        )

    # -------------------------------------------------
    # 4. Get AI shipment
    # -------------------------------------------------

    ai_evaluation = None

    if (
        ai_result
        and ai_result.get("best_match")
    ):

        ai_load_id = ai_result[
            "best_match"
        ]["load_id"]

        ai_shipment = db.query(
            Shipment
        ).filter(
            Shipment.load_id == ai_load_id
        ).first()

        ai_evaluation = evaluate_strategy(
            truck,
            ai_shipment,
            "AI"
        )

    # -------------------------------------------------
    # 5. Compare results
    # -------------------------------------------------

    comparison = {
        "same_truck_state": True,
        "baseline_selected": (
            baseline_evaluation is not None
        ),
        "ai_selected": (
            ai_evaluation is not None
        ),
        "same_load_selected": False
    }

    if baseline_evaluation and ai_evaluation:

        comparison["same_load_selected"] = (
            baseline_evaluation["load_id"]
            == ai_evaluation["load_id"]
        )

        comparison["distance_difference_km"] = round(
            baseline_evaluation["total_distance_km"]
            - ai_evaluation["total_distance_km"],
            2
        )

        comparison["cost_difference"] = round(
            baseline_evaluation["estimated_cost"]
            - ai_evaluation["estimated_cost"],
            2
        )

        comparison["profit_difference"] = round(
            ai_evaluation["estimated_profit"]
            - baseline_evaluation["estimated_profit"],
            2
        )

        comparison["revenue_difference"] = round(
            ai_evaluation["revenue"]
            - baseline_evaluation["revenue"],
            2
        )

        comparison["utilization_difference_percent"] = round(
            ai_evaluation[
                "capacity_utilization_percent"
            ]
            - baseline_evaluation[
                "capacity_utilization_percent"
            ],
            2
        )

        # -------------------------------------------------
        # Determine better strategy
        # -------------------------------------------------

        ai_profit = ai_evaluation[
            "estimated_profit"
        ]

        baseline_profit = baseline_evaluation[
            "estimated_profit"
        ]

        ai_distance = ai_evaluation[
            "total_distance_km"
        ]

        baseline_distance = baseline_evaluation[
            "total_distance_km"
        ]

        if (
            ai_profit > baseline_profit
            and ai_distance <= baseline_distance
        ):
            winner = "AI"

        elif (
            baseline_profit > ai_profit
            and baseline_distance <= ai_distance
        ):
            winner = "BASELINE"

        else:
            winner = "TRADE-OFF"

        comparison["winner"] = winner

    else:

        comparison["winner"] = "NO_COMPARISON"

    # -------------------------------------------------
    # 6. Final response
    # -------------------------------------------------

    return {
        "truck_id": truck_id,

        "experiment": {
            "type": "Controlled Baseline vs AI",
            "database_modified": False,
            "same_truck_state": True,
            "same_available_shipment_pool": True
        },

        "baseline": baseline_evaluation,

        "ai": ai_evaluation,

        "comparison": comparison
    }