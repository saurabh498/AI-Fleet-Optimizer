from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

import numpy as np

from ml.waiting_time_features import prepare_waiting_time_features


def calculate_metrics(y_test, predictions):
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

    return mae, rmse, mape


def train_and_evaluate():
    X, y = prepare_waiting_time_features()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    models = {
        "Linear Regression": LinearRegression(),

        "Random Forest": RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            max_depth=12,
            min_samples_split=4,
            n_jobs=-1
        ),

        "XGBoost": XGBRegressor(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1
        )
    }

    results = []

    for name, model in models.items():

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        mae, rmse, mape = calculate_metrics(
            y_test,
            predictions
        )

        results.append({
            "model": name,
            "mae": mae,
            "rmse": rmse,
            "mape": mape
        })

    results.sort(key=lambda item: item["mae"])

    print("=" * 70)
    print("WAITING-TIME MODEL COMPARISON")
    print("=" * 70)

    print(
        f"{'Model':<22}"
        f"{'MAE':>12}"
        f"{'RMSE':>12}"
        f"{'MAPE':>12}"
    )

    print("-" * 70)

    for result in results:

        print(
            f"{result['model']:<22}"
            f"{result['mae']:>12.4f}"
            f"{result['rmse']:>12.4f}"
            f"{result['mape']:>11.2f}%"
        )

    best = results[0]

    print("-" * 70)

    print("BEST MODEL")
    print("Model :", best["model"])
    print(f"MAE   : {best['mae']:.4f} hours")
    print(f"RMSE  : {best['rmse']:.4f} hours")
    print(f"MAPE  : {best['mape']:.2f}%")

    print("=" * 70)


if __name__ == "__main__":
    train_and_evaluate()