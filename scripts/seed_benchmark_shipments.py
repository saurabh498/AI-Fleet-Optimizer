'''Seed a realistic pool of benchmark shipments across 14 cities.'''

import argparse
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from backend.database.connection import SessionLocal
from backend.models.shipment import Shipment
from backend.services.route_optimizer import calculate_distance_km


CITIES_PATH = Path("data/india_cities.json")

CARGO_TYPES = [
    "Electronics", "Textiles", "Machinery",
    "Food Grains", "Pharma", "Auto Parts",
    "FMCG", "Chemicals",
]


def load_cities() -> list:
    with CITIES_PATH.open(encoding="utf-8-sig") as handle:
        return json.load(handle)["cities"]


def seed(count: int, seed_value: int, clear: bool):
    rng = random.Random(seed_value)
    cities = load_cities()

    db = SessionLocal()
    try:
        if clear:
            from backend.models.assignment import Assignment
            from backend.models.assignment_history import AssignmentHistory

            h = db.query(AssignmentHistory).delete()
            a = db.query(Assignment).delete()
            s = db.query(Shipment).delete()
            db.commit()
            print(f"Cleared {s} shipments, {a} assignments, {h} history rows.")

        existing = db.query(Shipment).count()
        if existing >= count:
            print(f"Already {existing} shipments. Use --clear to reseed.")
            return

        shipments = []
        now = datetime.utcnow()

        for _ in range(count):
            origin = rng.choice(cities)
            dest = rng.choice([c for c in cities if c["name"] != origin["name"]])

            straight_km = calculate_distance_km(
                origin["latitude"], origin["longitude"],
                dest["latitude"], dest["longitude"],
            )
            road_km = straight_km * 1.30

            weight = round(rng.uniform(2000, 12000), 0)

            # Revenue = base + weight component + distance component
            revenue = round(
                2000
                + weight * rng.uniform(1.2, 2.0)
                + road_km * rng.uniform(8, 15),
                -2,
            )

            pickup_start = now + timedelta(hours=rng.randint(1, 24))

            shipments.append(Shipment(
                pickup_city=origin["name"],
                pickup_latitude=origin["latitude"],
                pickup_longitude=origin["longitude"],
                destination_city=dest["name"],
                destination_latitude=dest["latitude"],
                destination_longitude=dest["longitude"],
                weight=weight,
                volume=None,
                cargo_type=rng.choice(CARGO_TYPES),
                pickup_start=pickup_start,
                pickup_deadline=pickup_start + timedelta(hours=6),
                delivery_deadline=pickup_start + timedelta(hours=48),
                revenue=revenue,
                status="available",
            ))

        db.add_all(shipments)
        db.commit()

        print(f"Seeded {len(shipments)} benchmark shipments.")
        print(f"  Seed: {seed_value}")
        print(f"  Cities: {len(cities)}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    seed(args.count, args.seed, args.clear)


if __name__ == "__main__":
    main()
