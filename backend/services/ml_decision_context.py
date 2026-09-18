from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.truck import Truck
from backend.models.shipment import Shipment
from backend.models.historical_shipment import HistoricalShipment

from backend.services.demand_prediction import predict_demand
from backend.services.waiting_time_prediction import predict_waiting_time

from ml.explainability import explain_demand_from_context


# -------------------------------------------------
# Core: ML predictions for an arbitrary city
# -------------------------------------------------

def _predict_for_city(city: str, db: Session) -> dict:
    '''
    Compute demand + waiting predictions for any city using
    the same historical/time features as the truck context.
    '''
    now = datetime.utcnow()
    hour = now.hour
    day_of_week = now.weekday()

    available_loads = (
        db.query(Shipment)
        .filter(
            Shipment.status == "available",
            Shipment.pickup_city == city,
        )
        .count()
    )

    historical_records = (
        db.query(HistoricalShipment)
        .filter(
            HistoricalShipment.city == city,
            HistoricalShipment.hour == hour,
            HistoricalShipment.day_of_week == day_of_week,
        )
        .all()
    )

    if not historical_records:
        historical_records = (
            db.query(HistoricalShipment)
            .filter(HistoricalShipment.city == city)
            .all()
        )

    if historical_records:
        completed_loads = round(
            sum(r.completed_loads for r in historical_records)
            / len(historical_records)
        )
        historical_average_demand = (
            sum(r.average_demand for r in historical_records)
            / len(historical_records)
        )
    else:
        completed_loads = 0
        historical_average_demand = 0.0

    demand_result = predict_demand(
        city=city,
        hour=hour,
        day_of_week=day_of_week,
        available_loads=available_loads,
        completed_loads=completed_loads,
    )
    predicted_demand = demand_result["predicted_demand"]

    waiting_result = predict_waiting_time(
        city=city,
        hour=hour,
        day_of_week=day_of_week,
        available_loads=available_loads,
        completed_loads=completed_loads,
        average_demand=predicted_demand,
    )
    predicted_waiting_time = waiting_result["predicted_waiting_time"]

    try:
        shap_explanation = explain_demand_from_context(
            city=city,
            hour=hour,
            day_of_week=day_of_week,
            available_loads=available_loads,
            completed_loads=completed_loads,
        )
    except Exception as exc:
        shap_explanation = {
            "summary": "SHAP explanation unavailable",
            "error": str(exc),
            "top_positive": [],
            "top_negative": [],
        }

    return {
        "city": city,
        "hour": hour,
        "day_of_week": day_of_week,
        "available_loads": available_loads,
        "completed_loads": completed_loads,
        "historical_average_demand": round(historical_average_demand, 2),
        "predicted_demand": predicted_demand,
        "predicted_waiting_time": predicted_waiting_time,
        "demand_model": demand_result["model_name"],
        "demand_model_version": demand_result["model_version"],
        "waiting_model": waiting_result["model_name"],
        "waiting_model_version": waiting_result["model_version"],
        "shap_explanation": shap_explanation,
    }


# -------------------------------------------------
# Public: ML context for an arbitrary city
# -------------------------------------------------

def build_ml_context_for_city(city: str, db: Session) -> dict:
    '''
    ML demand/waiting context for any city, independent of trucks.
    Used by the benchmark to score shipment destinations.
    '''
    return _predict_for_city(city, db)


# -------------------------------------------------
# Public: ML context for a specific truck
# -------------------------------------------------

def build_ml_decision_context(truck_id: int, db: Session):
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
            "reason": "Truck current city is not available",
        }

    context = _predict_for_city(truck.current_city, db)
    context["truck_id"] = truck_id
    context["available"] = True
    return context
