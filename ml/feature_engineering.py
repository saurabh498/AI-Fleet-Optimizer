import pandas as pd

from backend.database.connection import SessionLocal
from backend.models.historical_shipment import HistoricalShipment


FEATURE_COLUMNS = [
    "city",
    "hour",
    "day_of_week",
    "available_loads",
    "completed_loads"
]

TARGET_COLUMN = "average_demand"


def load_historical_data():
    db = SessionLocal()

    try:
        records = db.query(HistoricalShipment).all()

        data = [
            {
                "date": record.date,
                "city": record.city,
                "hour": record.hour,
                "day_of_week": record.day_of_week,
                "available_loads": record.available_loads,
                "completed_loads": record.completed_loads,
                "average_waiting_time": record.average_waiting_time,
                "average_demand": record.average_demand
            }
            for record in records
        ]

        return pd.DataFrame(data)

    finally:
        db.close()


def prepare_features():
    df = load_historical_data()

    if df.empty:
        raise ValueError(
            "Historical shipment dataset is empty."
        )

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    X = pd.get_dummies(
        X,
        columns=["city"],
        dtype=int
    )

    return X, y


if __name__ == "__main__":
    X, y = prepare_features()

    print("=" * 50)
    print("FEATURE ENGINEERING")
    print("=" * 50)

    print("Dataset rows :", len(X))
    print("Feature count:", len(X.columns))
    print("Target       :", TARGET_COLUMN)

    print("\nFeatures:")
    for column in X.columns:
        print(" -", column)

    print("\nTarget statistics:")
    print(y.describe())

    print("=" * 50)