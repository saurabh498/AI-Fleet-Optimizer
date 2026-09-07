from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path("ml/models/baseline_waiting_time_model.joblib")


def load_waiting_time_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Waiting-time model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_waiting_time(
    city: str,
    hour: int,
    day_of_week: int,
    available_loads: int,
    completed_loads: int,
    average_demand: float
):
    package = load_waiting_time_model()

    model = package["model"]
    feature_columns = package["feature_columns"]

    input_data = pd.DataFrame([{
        "city": city,
        "hour": hour,
        "day_of_week": day_of_week,
        "available_loads": available_loads,
        "completed_loads": completed_loads,
        "average_demand": average_demand
    }])

    input_data = pd.get_dummies(
        input_data,
        columns=["city"],
        dtype=int
    )

    input_data = input_data.reindex(
        columns=feature_columns,
        fill_value=0
    )

    prediction = float(
        model.predict(input_data)[0]
    )

    return {
        "predicted_waiting_time": round(
            max(0.0, prediction),
            2
        ),
        "model_name": package["model_name"],
        "model_version": package["model_version"]
    }


if __name__ == "__main__":
    result = predict_waiting_time(
        city="Mumbai",
        hour=10,
        day_of_week=0,
        available_loads=5,
        completed_loads=3,
        average_demand=13.55
    )

    print("=" * 50)
    print("WAITING-TIME PREDICTION")
    print("=" * 50)
    print(result)
    print("=" * 50)