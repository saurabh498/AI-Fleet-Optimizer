from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import joblib

from ml.feature_engineering import prepare_features


MODEL_PATH = Path("ml/models/baseline_demand_model.joblib")


def train_baseline_model():
    X, y = prepare_features()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    non_zero_actual = y_test != 0

    if non_zero_actual.any():
        mape = np.mean(
            np.abs(
                (y_test[non_zero_actual] - predictions[non_zero_actual])
                / y_test[non_zero_actual]
            )
        ) * 100
    else:
        mape = 0.0

    return {
        "model": model,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "training_samples": len(X_train),
        "testing_samples": len(X_test),
        "feature_count": len(X.columns),
        "feature_columns": list(X.columns)
    }


def save_model(result):
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    model_package = {
        "model": result["model"],
        "feature_columns": result["feature_columns"],
        "model_name": "Linear Regression",
        "model_version": "baseline-v1",
        "target": "average_demand",
        "mae": result["mae"],
        "rmse": result["rmse"],
        "mape": result["mape"]
    }

    joblib.dump(model_package, MODEL_PATH)

    return MODEL_PATH


if __name__ == "__main__":
    result = train_baseline_model()
    model_path = save_model(result)

    print("=" * 50)
    print("BASELINE DEMAND MODEL")
    print("=" * 50)
    print("Model              : Linear Regression")
    print("Model version      : baseline-v1")
    print("Training samples   :", result["training_samples"])
    print("Testing samples    :", result["testing_samples"])
    print("Feature count      :", result["feature_count"])

    print("\nEvaluation:")
    print("MAE                :", round(result["mae"], 4))
    print("RMSE               :", round(result["rmse"], 4))
    print("MAPE               :", round(result["mape"], 2), "%")

    print("\nModel saved to     :", model_path)

    print("=" * 50)