from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "xgboost_demand_model.joblib"


def load_demand_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Demand model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_demand(
    city: str,
    hour: int,
    day_of_week: int,
    available_loads: int,
    completed_loads: int
):
    package = load_demand_model()

    model = package["model"]
    feature_columns = package["feature_columns"]

    input_data = pd.DataFrame(
        [{
            "city": city,
            "hour": hour,
            "day_of_week": day_of_week,
            "available_loads": available_loads,
            "completed_loads": completed_loads
        }]
    )

    input_data = pd.get_dummies(
        input_data,
        columns=["city"],
        dtype=int
    )

    input_data = input_data.reindex(
        columns=feature_columns,
        fill_value=0
    )

    prediction = float(model.predict(input_data)[0])

    return {
        "predicted_demand": round(max(0.0, prediction), 2),
        "model_name": package["model_name"],
        "model_version": package["model_version"]
    }