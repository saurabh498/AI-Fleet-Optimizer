
"""
SHAP-based explainability for ML models.

Given a demand context (city, hour, etc.), returns the
top-N features that pushed the prediction up or down,
in plain English.
"""

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap


DEMAND_MODEL_PATH = Path("ml/models/xgboost_demand_model.joblib")

FRIENDLY_NAMES = {
    "hour": "hour of day",
    "day_of_week": "day of week",
    "available_loads": "available loads",
    "completed_loads": "completed loads",
}


@lru_cache(maxsize=1)
def _load_demand_model():
    if not DEMAND_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Demand model not found at {DEMAND_MODEL_PATH}. "
            "Train it first with: python -m ml.xgboost_demand_model"
        )
    package = joblib.load(DEMAND_MODEL_PATH)
    return package["model"], package["feature_columns"]


@lru_cache(maxsize=1)
def _get_explainer():
    model, _ = _load_demand_model()
    return shap.TreeExplainer(model)


def _friendly(feature: str) -> str:
    if feature.startswith("city_"):
        return f"city {feature.removeprefix('city_')}"
    return FRIENDLY_NAMES.get(feature, feature)


def explain_demand_prediction(
    feature_row: dict,
    top_n: int = 5
) -> dict:
    """
    Compute SHAP values for a single pre-built feature row.
    `feature_row` must contain every column the model saw
    during training.
    """

    model, feature_columns = _load_demand_model()
    explainer = _get_explainer()

    missing = [c for c in feature_columns if c not in feature_row]
    if missing:
        raise ValueError(f"Missing features for SHAP: {missing}")

    ordered = {c: [feature_row[c]] for c in feature_columns}
    df = pd.DataFrame(ordered)

    shap_values = explainer.shap_values(df)

    if hasattr(shap_values, "values"):
        values = np.array(shap_values.values)[0]
        base = float(np.array(shap_values.base_values).flatten()[0])
    else:
        values = np.array(shap_values)[0]
        base = float(explainer.expected_value)

    predicted = float(model.predict(df)[0])

    contributions = [
        {
            "feature": _friendly(feature_columns[i]),
            "raw_feature": feature_columns[i],
            "value": float(df.iloc[0, i]),
            "impact": round(float(values[i]), 4),
        }
        for i in range(len(feature_columns))
    ]

    positives = sorted(
        [c for c in contributions if c["impact"] > 0],
        key=lambda x: x["impact"],
        reverse=True,
    )[:top_n]

    negatives = sorted(
        [c for c in contributions if c["impact"] < 0],
        key=lambda x: x["impact"],
    )[:top_n]

    if positives:
        top = positives[0]
        summary = (
            f"Prediction of {predicted:.2f} driven mostly by "
            f"{top['feature']} ({top['value']:.2f}), which added "
            f"{top['impact']:+.2f}."
        )
    elif negatives:
        top = negatives[0]
        summary = (
            f"Prediction of {predicted:.2f} pulled down mostly by "
            f"{top['feature']} ({top['value']:.2f}), which subtracted "
            f"{abs(top['impact']):.2f}."
        )
    else:
        summary = (
            f"Prediction of {predicted:.2f} with no dominant "
            "contributors."
        )

    return {
        "base_value": round(base, 4),
        "predicted_value": round(predicted, 4),
        "top_positive": positives,
        "top_negative": negatives,
        "summary": summary,
    }


def explain_demand_from_context(
    city: str,
    hour: int,
    day_of_week: int,
    available_loads: int,
    completed_loads: int,
    top_n: int = 5
) -> dict:
    """
    Build the model's feature row from the raw demand
    context (as used by ml_decision_context) and compute
    SHAP values.

    Handles the city one-hot encoding automatically by
    reading the feature schema from the trained model.
    """

    _, feature_columns = _load_demand_model()

    row = {
        "hour": hour,
        "day_of_week": day_of_week,
        "available_loads": available_loads,
        "completed_loads": completed_loads,
    }

    for col in feature_columns:
        if col.startswith("city_"):
            city_name = col.removeprefix("city_")
            row[col] = 1 if city_name == city else 0
        elif col not in row:
            row[col] = 0

    return explain_demand_prediction(row, top_n=top_n)
