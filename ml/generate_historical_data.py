from datetime import date, timedelta
import random

from backend.database.connection import SessionLocal
from backend.models.historical_shipment import HistoricalShipment


CITIES = [
    "Mumbai",
    "Pune",
    "Ahmedabad",
    "Surat",
    "Delhi",
    "Gurgaon",
    "Jaipur",
    "Indore",
    "Bhopal",
    "Hyderabad",
    "Bengaluru",
    "Chennai",
    "Kolkata",
    "Nagpur"
]

TOTAL_RECORDS = 5000

START_DATE = date(2026, 1, 1)


def generate_record(index: int):
    record_date = START_DATE + timedelta(days=index // (len(CITIES) * 24))

    city = random.choice(CITIES)

    hour = random.randint(0, 23)

    day_of_week = record_date.weekday()

    # Base demand
    demand = random.uniform(5, 25)

    # Morning and evening logistics peaks
    if 7 <= hour <= 10:
        demand += random.uniform(8, 18)

    elif 17 <= hour <= 21:
        demand += random.uniform(10, 20)

    # Weekday demand is generally higher
    if day_of_week < 5:
        demand += random.uniform(3, 8)

    # Weekend reduction
    else:
        demand -= random.uniform(1, 5)

    # City activity variation
    city_factor = {
        "Mumbai": 1.25,
        "Delhi": 1.25,
        "Pune": 1.10,
        "Bengaluru": 1.15,
        "Hyderabad": 1.05,
        "Ahmedabad": 1.05,
        "Surat": 1.00,
        "Chennai": 1.05,
        "Kolkata": 1.00,
        "Jaipur": 0.90,
        "Gurgaon": 1.10,
        "Indore": 0.90,
        "Bhopal": 0.85,
        "Nagpur": 0.95
    }

    demand *= city_factor[city]

    demand = max(1, demand)

    available_loads = max(
        1,
        int(demand + random.uniform(2, 12))
    )

    completion_rate = random.uniform(0.65, 0.95)

    completed_loads = min(
        available_loads,
        max(0, int(available_loads * completion_rate))
    )

    average_waiting_time = max(
        0.25,
        random.uniform(0.5, 4.0)
        - (demand * 0.03)
    )

    average_demand = round(
         max(0, demand + random.uniform(-2, 2)),
         2
    )

    return HistoricalShipment(
        date=record_date,
        city=city,
        hour=hour,
        day_of_week=day_of_week,
        available_loads=available_loads,
        completed_loads=completed_loads,
        average_waiting_time=round(
            average_waiting_time,
            2
        ),
        average_demand=average_demand
    )


def generate_dataset():
    db = SessionLocal()

    try:
        existing_count = db.query(
            HistoricalShipment
        ).count()

        if existing_count > 0:
            print(
                f"Historical dataset already contains "
                f"{existing_count} records."
            )
            print("No new records generated.")
            return

        records = []

        for index in range(TOTAL_RECORDS):
            records.append(
                generate_record(index)
            )

        db.bulk_save_objects(records)
        db.commit()

        print("=" * 50)
        print("HISTORICAL DATASET GENERATED")
        print("=" * 50)
        print(f"Records created : {len(records)}")
        print(f"Cities used     : {len(CITIES)}")
        print(f"Start date      : {START_DATE}")
        print("=" * 50)

    except Exception as exc:
        db.rollback()
        print("Dataset generation failed:")
        print(exc)

    finally:
        db.close()


if __name__ == "__main__":
    generate_dataset()