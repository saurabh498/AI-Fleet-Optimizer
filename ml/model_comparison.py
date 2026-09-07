from ml.baseline_demand_model import train_baseline_model
from ml.random_forest_demand_model import train_random_forest_model
from ml.xgboost_demand_model import train_xgboost_model


def compare_models():
    baseline = train_baseline_model()
    random_forest = train_random_forest_model()
    xgboost = train_xgboost_model()

    models = [
        {
            "name": "Linear Regression",
            "mae": baseline["mae"],
            "rmse": baseline["rmse"],
            "mape": baseline["mape"]
        },
        {
            "name": "Random Forest",
            "mae": random_forest["mae"],
            "rmse": random_forest["rmse"],
            "mape": random_forest["mape"]
        },
        {
            "name": "XGBoost",
            "mae": xgboost["mae"],
            "rmse": xgboost["rmse"],
            "mape": xgboost["mape"]
        }
    ]

    best_model = min(models, key=lambda item: item["mae"])

    print("=" * 70)
    print("DEMAND MODEL COMPARISON")
    print("=" * 70)

    print(
        f"{'Model':<22}"
        f"{'MAE':>12}"
        f"{'RMSE':>12}"
        f"{'MAPE (%)':>12}"
    )

    print("-" * 70)

    for model in models:
        print(
            f"{model['name']:<22}"
            f"{model['mae']:>12.4f}"
            f"{model['rmse']:>12.4f}"
            f"{model['mape']:>12.2f}"
        )

    print("-" * 70)

    print("\nBest model based on MAE:")
    print("Model :", best_model["name"])
    print("MAE   :", round(best_model["mae"], 4))
    print("RMSE  :", round(best_model["rmse"], 4))
    print("MAPE  :", round(best_model["mape"], 2), "%")

    print("=" * 70)

    return models, best_model


if __name__ == "__main__":
    compare_models()