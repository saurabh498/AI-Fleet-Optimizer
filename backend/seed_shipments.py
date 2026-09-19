from datetime import datetime, timedelta

from backend.database.connection import SessionLocal
from backend.models.shipment import Shipment


def seed_shipments():
    db = SessionLocal()

    try:
        now = datetime.now()

        shipments = [
            Shipment(
                pickup_city="Mumbai",
                pickup_latitude=19.0760,
                pickup_longitude=72.8777,
                destination_city="Pune",
                destination_latitude=18.5204,
                destination_longitude=73.8567,
                weight=3000,
                volume=12,
                cargo_type="Electronics",
                pickup_start=now + timedelta(hours=2),
                pickup_deadline=now + timedelta(hours=8),
                delivery_deadline=now + timedelta(hours=16),
                revenue=28000,
                status="available",
            ),

            Shipment(
                pickup_city="Pune",
                pickup_latitude=18.5204,
                pickup_longitude=73.8567,
                destination_city="Hyderabad",
                destination_latitude=17.3850,
                destination_longitude=78.4867,
                weight=9000,
                volume=35,
                cargo_type="Industrial Equipment",
                pickup_start=now + timedelta(hours=4),
                pickup_deadline=now + timedelta(hours=12),
                delivery_deadline=now + timedelta(hours=30),
                revenue=52000,
                status="available",
            ),

            Shipment(
                pickup_city="Nashik",
                pickup_latitude=20.0059,
                pickup_longitude=73.7910,
                destination_city="Mumbai",
                destination_latitude=19.0760,
                destination_longitude=72.8777,
                weight=4000,
                volume=16,
                cargo_type="Food Products",
                pickup_start=now + timedelta(hours=3),
                pickup_deadline=now + timedelta(hours=10),
                delivery_deadline=now + timedelta(hours=18),
                revenue=34000,
                status="available",
            ),

            Shipment(
                pickup_city="Ahmedabad",
                pickup_latitude=23.0225,
                pickup_longitude=72.5714,
                destination_city="Mumbai",
                destination_latitude=19.0760,
                destination_longitude=72.8777,
                weight=7000,
                volume=28,
                cargo_type="Textiles",
                pickup_start=now + timedelta(hours=5),
                pickup_deadline=now + timedelta(hours=14),
                delivery_deadline=now + timedelta(hours=30),
                revenue=50000,
                status="available",
            ),

            Shipment(
                pickup_city="Surat",
                pickup_latitude=21.1702,
                pickup_longitude=72.8311,
                destination_city="Pune",
                destination_latitude=18.5204,
                destination_longitude=73.8567,
                weight=3500,
                volume=14,
                cargo_type="Garments",
                pickup_start=now + timedelta(hours=3),
                pickup_deadline=now + timedelta(hours=11),
                delivery_deadline=now + timedelta(hours=24),
                revenue=30000,
                status="available",
            ),

            Shipment(
                pickup_city="Indore",
                pickup_latitude=22.7196,
                pickup_longitude=75.8577,
                destination_city="Mumbai",
                destination_latitude=19.0760,
                destination_longitude=72.8777,
                weight=8000,
                volume=30,
                cargo_type="Automotive Parts",
                pickup_start=now + timedelta(hours=6),
                pickup_deadline=now + timedelta(hours=15),
                delivery_deadline=now + timedelta(hours=32),
                revenue=48000,
                status="available",
            ),

            Shipment(
                pickup_city="Bhopal",
                pickup_latitude=23.2599,
                pickup_longitude=77.4126,
                destination_city="Pune",
                destination_latitude=18.5204,
                destination_longitude=73.8567,
                weight=6000,
                volume=24,
                cargo_type="Machinery",
                pickup_start=now + timedelta(hours=4),
                pickup_deadline=now + timedelta(hours=13),
                delivery_deadline=now + timedelta(hours=30),
                revenue=46000,
                status="available",
            ),

            Shipment(
                pickup_city="Nagpur",
                pickup_latitude=21.1458,
                pickup_longitude=79.0882,
                destination_city="Hyderabad",
                destination_latitude=17.3850,
                destination_longitude=78.4867,
                weight=5000,
                volume=20,
                cargo_type="Consumer Goods",
                pickup_start=now + timedelta(hours=5),
                pickup_deadline=now + timedelta(hours=14),
                delivery_deadline=now + timedelta(hours=28),
                revenue=42000,
                status="available",
            ),
        ]

        db.add_all(shipments)
        db.commit()

        print(f"Successfully seeded {len(shipments)} shipments.")

        for shipment in shipments:
            print(
                f"Load #{shipment.load_id}: "
                f"{shipment.pickup_city} -> {shipment.destination_city} | "
                f"{shipment.weight} kg | "
                f"₹{shipment.revenue}"
            )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_shipments()