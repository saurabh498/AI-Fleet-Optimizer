from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.api.deps import get_current_user
from backend.models.prediction import Prediction
from backend.schemas.demand_prediction import (
    DemandPredictionRequest,
    DemandPredictionResponse
)
from backend.services.demand_prediction import predict_demand


router = APIRouter(
    prefix="/demand",
    tags=["Demand Prediction"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/predict",
    response_model=DemandPredictionResponse
)
def predict_demand_api(
    request: DemandPredictionRequest,
    db: Session = Depends(get_db)
):
    result = predict_demand(
        city=request.city,
        hour=request.hour,
        day_of_week=request.day_of_week,
        available_loads=request.available_loads,
        completed_loads=request.completed_loads
    )

    prediction = Prediction(
        truck_id=request.truck_id,
        location=request.city,
        predicted_demand=result["predicted_demand"],
        predicted_waiting_time=0.0
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return result

@router.get("/history")
def get_prediction_history(
    db: Session = Depends(get_db)
):
    predictions = (
        db.query(Prediction)
        .order_by(Prediction.prediction_time.desc())
        .all()
    )

    return [
        {
            "prediction_id": prediction.prediction_id,
            "truck_id": prediction.truck_id,
            "location": prediction.location,
            "predicted_demand": prediction.predicted_demand,
            "predicted_waiting_time": prediction.predicted_waiting_time,
            "prediction_time": prediction.prediction_time
        }
        for prediction in predictions
    ]