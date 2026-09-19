"""
Deterministic generator for the historical shipment dataset.

Uses real Indian city economic data (see data/india_cities.json)
combined with real freight traffic patterns published by NHAI
(hour-of-day curve, weekly curve, seasonal effects).

Every record is fully reproducible given the same seed, and
every input traces to a public source. See docs/data_sources.md.

Usage:
    python -m ml.generate_historical_data                # default: 5000 records
    python -m ml.generate_historical_data --full-year    # 365 days x 14 cities x 24 hours
    python -m ml.generate_historical_data --force        # wipe + regenerate
    python -m ml.generate_historical_data --seed 42      # reproducible seed
"""

import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

from backend.database.connection import SessionLocal
from backend.models.historical_shipment import HistoricalShipment


CITIES_PATH = Path("data/india_cities.json")

START_DATE = date(2024, 1, 1)
DAYS_IN_YEAR = 365


# -------------------------------------------------
# Real freight traffic patterns (NHAI-published)
# -------------------------------------------------

# Hour-of-day freight intensity (24 entries, index 0-23)
# Peaks at 6-9am (dispatch window) and 17-21pm (return window)
HOUR_FACTOR = [
    0.20, 0.20, 0.22, 0.25, 0.30, 0.45,   # 00-05
    0.90, 1.40, 1.45, 1.30, 1.05, 0.95,   # 06-11
    0.85, 0.80, 0.82, 0.85, 0.95, 1.30,   # 12-17
    1.35, 1.25, 1.10, 0.85, 0.55, 0.35,   # 18-23
]

# Day-of-week multiplier (Monday=0 ... Sunday=6)
DOW_FACTOR = [1.00, 1.00, 1.02, 1.05, 1.10, 0.85, 0.55]

# Seasonal multiplier (month 1-12)
MONTH_FACTOR = [
    1.00, 1.00, 1.05, 1.05, 1.03, 0.92,   # Jan-Jun (monsoon begins)
    0.88, 0.90, 0.95, 1.20, 1.22, 1.10,   # Jul-Dec (festival spike Oct-Nov)
]


# -------------------------------------------------
# Load city data
# -------------------------------------------------

def load_cities() -> list:
    with CITIES_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data["cities"]


# -------------------------------------------------
# Core demand calculation
# -------------------------------------------------

def compute_demand(
    city: dict,
    record_date: date,
    hour: int,
    noise: float
) -> float:
    """
    Compute realistic demand for a single city/hour/day.

    Formula:
        demand = BASE
               * city_industrial_index
               * hour_factor
               * dow_factor
               * month_factor
               * (1 + noise)
    """

    BASE = 18.0  # national average loads available per city-hour

    demand = BASE
    demand *= city["industrial_index"]
    demand *= HOUR_FACTOR[hour]
    demand *= DOW_FACTOR[record_date.weekday()]
    demand *= MONTH_FACTOR[record_date.month - 1]
    demand *= (1.0 + noise)

    return max(1.0, demand)


def compute_waiting_time(
    demand: float,
    noise: float
) -> float:
    """
    Higher demand -> shorter waiting time.
    Real-world observation: waiting time is inversely
    correlated with available loads (logistic relationship).
    """

    base_wait = 6.0 / (1.0 + demand / 10.0)
    return max(0.25, base_wait * (1.0 + noise))


def compute_completion_rate(
    record_date: date,
    hour: int,
    noise: float
) -> float:
    """
    Completion rate varies with time of day and weekday.
    NHAI data shows peak-hour throughput is higher.
    """

    base = 0.80
    if 6 <= hour <= 10:
        base = 0.88
    elif 17 <= hour <= 21:
        base = 0.85
    elif 0 <= hour <= 4:
        base = 0.60

    if record_date.weekday() >= 5:
        base -= 0.05

    return min(0.97, max(0.40, base * (1.0 + noise)))


# -------------------------------------------------
# Record builder
# -------------------------------------------------

def build_record(
    city: dict,
    record_date: date,
    hour: int,
    rng: random.Random
) -> HistoricalShipment:

    hour_noise = rng.uniform(-0.15, 0.15)
    wait_noise = rng.uniform(-0.20, 0.20)
    comp_noise = rng.uniform(-0.08, 0.08)

    demand = compute_demand(city, record_date, hour, hour_noise)
    waiting_time = compute_waiting_time(demand, wait_noise)
    completion_rate = compute_completion_rate(record_date, hour, comp_noise)

    available_loads = max(1, int(round(demand + rng.uniform(0, 5))))
    completed_loads = min(
        available_loads,
        max(0, int(round(available_loads * completion_rate))),
    )

    return HistoricalShipment(
        date=record_date,
        city=city["name"],
        hour=hour,
        day_of_week=record_date.weekday(),
        available_loads=available_loads,
        completed_loads=completed_loads,
        average_waiting_time=round(waiting_time, 2),
        average_demand=round(demand, 2),
    )


# -------------------------------------------------
# Dataset generators
# -------------------------------------------------

def generate_compact(rng: random.Random, total: int, cities: list) -> list:
    """Original style: total random records across cities."""
    records = []
    for _ in range(total):
        day_offset = rng.randint(0, DAYS_IN_YEAR - 1)
        record_date = START_DATE + timedelta(days=day_offset)
        hour = rng.randint(0, 23)
        city = rng.choice(cities)
        records.append(build_record(city, record_date, hour, rng))
    return records


def generate_full_year(rng: random.Random, cities: list) -> list:
    """Full 365-day x 24-hour x all cities grid."""
    records = []
    for day_offset in range(DAYS_IN_YEAR):
        record_date = START_DATE + timedelta(days=day_offset)
        for hour in range(24):
            for city in cities:
                records.append(
                    build_record(city, record_date, hour, rng)
                )
    return records


# -------------------------------------------------
# CLI entry
# -------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full-year",
        action="store_true",
        help="Generate full 365 x 24 x 14 grid (~122k rows).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing rows before generating.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42).",
    )
    parser.add_argument(
        "--total",
        type=int,
        default=5000,
        help="Record count in compact mode (default: 5000).",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    cities = load_cities()

    db = SessionLocal()
    try:
        existing = db.query(HistoricalShipment).count()

        if existing > 0 and not args.force:
            print(f"Historical dataset already has {existing} rows.")
            print("Use --force to wipe and regenerate.")
            return

        if existing > 0 and args.force:
            print(f"Deleting {existing} existing rows...")
            db.query(HistoricalShipment).delete()
            db.commit()

        if args.full_year:
            records = generate_full_year(rng, cities)
            mode = "full-year"
        else:
            records = generate_compact(rng, args.total, cities)
            mode = "compact"

        print(f"Generated {len(records)} records (mode: {mode}, seed: {args.seed})")
        db.bulk_save_objects(records)
        db.commit()

        print("=" * 60)
        print("HISTORICAL DATASET GENERATED")
        print("=" * 60)
        print(f"Mode            : {mode}")
        print(f"Seed            : {args.seed}")
        print(f"Records created : {len(records)}")
        print(f"Cities used     : {len(cities)}")
        print(f"Start date      : {START_DATE}")
        print("=" * 60)

    except Exception as exc:
        db.rollback()
        print("Dataset generation failed:")
        print(exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()