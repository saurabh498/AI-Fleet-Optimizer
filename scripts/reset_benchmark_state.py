'''Reset DB to a clean benchmark-ready state.

Deletes (in FK-safe order):
    assignment_history
    assignments
    truck_locations
    shipments

Then resets all trucks to status='available', load=0, no destination.
'''

from backend.database.connection import SessionLocal
from backend.models.assignment import Assignment
from backend.models.assignment_history import AssignmentHistory
from backend.models.shipment import Shipment
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation


def reset():
    db = SessionLocal()
    try:
        h = db.query(AssignmentHistory).delete()
        a = db.query(Assignment).delete()
        l = db.query(TruckLocation).delete()
        s = db.query(Shipment).delete()
        db.commit()

        trucks = db.query(Truck).all()
        for t in trucks:
            t.status = "available"
            t.current_load = 0
            t.destination = None
        db.commit()

        print("Reset complete:")
        print(f"  assignment_history : {h}")
        print(f"  assignments        : {a}")
        print(f"  truck_locations    : {l}")
        print(f"  shipments          : {s}")
        print(f"  trucks reset       : {len(trucks)}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset()
