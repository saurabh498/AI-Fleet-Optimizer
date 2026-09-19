"""Delete all rows from the historical_shipments table."""

from backend.database.connection import SessionLocal
from backend.models.historical_shipment import HistoricalShipment


def main():
    db = SessionLocal()
    try:
        count = db.query(HistoricalShipment).count()
        if count == 0:
            print("Historical dataset is already empty.")
            return

        print(f"Deleting {count} rows...")
        db.query(HistoricalShipment).delete()
        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
