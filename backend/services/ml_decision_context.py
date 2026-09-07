from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.truck import Truck
from backend.models.shipment import Shipment
from backend.models.historical_shipment import HistoricalShipment

from backend.services.demand_prediction import predict_demand
from backend.services.waiting_time_prediction import predict_waiting_time


def build_ml_decision_context(
    truck_id: int,
    db: Session
):
    """
    Build ML context for the assignment decision engine.

    Uses the truck's current city, current time context,
    current available loads, and historical statistics
    for the same city/hour/day-of-week.
    """

    # -------------------------------------------------
    # Get truck
    # -------------------------------------------------

    truck = (
        db.query(Truck)
        .filter(Truck.truck_id == truck_id)
        .first()
    )

    if not truck:
        return None

    if not truck.current_city:
        return {
            "truck_id": truck_id,
            "available": False,
            "reason": "Truck current city is not available"
        }

    city = truck.current_city

    # -------------------------------------------------
    # Current time context
    # -------------------------------------------------

    now = datetime.utcnow()

    hour = now.hour
    day_of_week = now.weekday()

    # -------------------------------------------------
    # Current available loads in truck's city
    # -------------------------------------------------

    available_loads = (
        db.query(Shipment)
        .filter(
            Shipment.status == "available",
            Shipment.pickup_city == city
        )
        .count()
    )

    # -------------------------------------------------
    # Historical context
    #
    # Match same city + hour + day of week.
    # -------------------------------------------------

    historical_records = (
        db.query(HistoricalShipment)
        .filter(
            HistoricalShipment.city == city,
            HistoricalShipment.hour == hour,
            HistoricalShipment.day_of_week == day_of_week
        )
        .all()
    )

    # -------------------------------------------------
    # Fallback if exact time context has no records
    # -------------------------------------------------

    if not historical_records:

        historical_records = (
            db.query(HistoricalShipment)
            .filter(
                HistoricalShipment.city == city
            )
            .all()
        )

    # -------------------------------------------------
    # Historical statistics
    # -------------------------------------------------

    if historical_records:

        completed_loads = round(
            sum(
                record.completed_loads
                for record in historical_records
            )
            / len(historical_records)
        )

        historical_average_demand = (
            sum(
                record.average_demand
                for record in historical_records
            )
            / len(historical_records)
        )

    else:

        completed_loads = 0
        historical_average_demand = 0.0

    # -------------------------------------------------
    # Demand prediction
    # -------------------------------------------------

    demand_result = predict_demand(
        city=city,
        hour=hour,
        day_of_week=day_of_week,
        available_loads=available_loads,
        completed_loads=completed_loads
    )

    predicted_demand = demand_result[
        "predicted_demand"
    ]

    # -------------------------------------------------
    # Waiting-time prediction
    # -------------------------------------------------

    waiting_result = predict_waiting_time(
        city=city,
        hour=hour,
        day_of_week=day_of_week,
        available_loads=available_loads,
        completed_loads=completed_loads,
        average_demand=predicted_demand
    )

    predicted_waiting_time = waiting_result[
        "predicted_waiting_time"
    ]

    # -------------------------------------------------
    # Final ML context
    # -------------------------------------------------

    return {
        "truck_id": truck_id,
        "available": True,
        "city": city,
        "hour": hour,
        "day_of_week": day_of_week,
        "available_loads": available_loads,
        "completed_loads": completed_loads,
        "historical_average_demand": round(
            historical_average_demand,
            2
        ),
        "predicted_demand": predicted_demand,
        "predicted_waiting_time": predicted_waiting_time,
        "demand_model": demand_result["model_name"],
        "demand_model_version": demand_result[
            "model_version"
        ],
        "waiting_model": waiting_result["model_name"],
        "waiting_model_version": waiting_result[
            "model_version"
        ]
    }