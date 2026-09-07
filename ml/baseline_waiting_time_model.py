from pathlib import Path

import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
import numpy as np

from ml.waiting_time_features import prepare_waiting_time_features


MODEL_PATH = Path("ml/models/baseline_waiting_time_model.joblib")


def train_model():
    X, y = prepare_waiting_time_features()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    non_zero_actual = y_test != 0
    mape = (
        np.mean(
            np.abs(
                (y_test[non_zero_actual] - predictions[non_zero_actual])
                / y_test[non_zero_actual]
            )
        ) * 100
    )

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    package = {
        "model": model,
        "feature_columns": list(X.columns),
        "model_name": "Linear Regression",
        "model_version": "baseline-waiting-v1",
        "target": "average_waiting_time",
        "metrics": {
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "MAPE": round(mape, 2)
        }
    }

    joblib.dump(package, MODEL_PATH)

    print("=" * 50)
    print("BASELINE WAITING-TIME MODEL")
    print("=" * 50)

    print("Training rows :", len(X_train))
    print("Testing rows  :", len(X_test))
    print("Features      :", len(X.columns))

    print("\nModel         : Linear Regression")
    print(f"MAE           : {mae:.4f} hours")
    print(f"RMSE          : {rmse:.4f} hours")
    print(f"MAPE          : {mape:.2f}%")

    print("\nModel saved to:")
    print(MODEL_PATH)

    print("=" * 50)


if __name__ == "__main__":
    train_model()