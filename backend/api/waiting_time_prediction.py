from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.api.deps import get_current_user
from backend.models.prediction import Prediction
from backend.schemas.waiting_time_prediction import (
    WaitingTimePredictionRequest,
    WaitingTimePredictionResponse
)
from backend.services.waiting_time_prediction import (
    predict_waiting_time
)


router = APIRouter(
    prefix="/waiting-time",
    tags=["Waiting Time Prediction"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/predict",
    response_model=WaitingTimePredictionResponse
)
def predict_waiting_time_api(
    request: WaitingTimePredictionRequest,
    db: Session = Depends(get_db)
):
    result = predict_waiting_time(
        city=request.city,
        hour=request.hour,
        day_of_week=request.day_of_week,
        available_loads=request.available_loads,
        completed_loads=request.completed_loads,
        average_demand=request.average_demand
    )

    prediction = Prediction(
        truck_id=request.truck_id,
        location=request.city,
        predicted_demand=request.average_demand,
        predicted_waiting_time=result["predicted_waiting_time"]
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return result

@router.get("/history")
def get_waiting_prediction_history(
    db: Session = Depends(get_db)
):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.predicted_waiting_time > 0)
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