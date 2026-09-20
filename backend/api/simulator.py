"""
Server-side GPS simulator.

Runs a full route simulation for all in_transit trucks
in a FastAPI BackgroundTask. The frontend triggers it
and polls for updated truck positions.
"""

import time

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, require_role
from backend.database.connection import SessionLocal, get_db
from backend.models.assignment import Assignment
from backend.models.shipment import Shipment
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation


router = APIRouter(
    prefix="/simulator",
    tags=["Simulator"],
    dependencies=[Depends(get_current_user)],
)


STEPS = 8
INTERVAL_SECONDS = 2.0


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _write_location(db, truck, lat, lon, speed):
    from datetime import datetime

    location = TruckLocation(
        truck_id=truck.truck_id,
        timestamp=datetime.utcnow(),
        latitude=round(lat, 6),
        longitude=round(lon, 6),
        speed=speed,
    )
    db.add(location)

    truck.current_latitude = lat
    truck.current_longitude = lon

    db.commit()


def _run_full_simulation(truck_ids: list):
    """
    Background task: moves each truck through its route,
    runs arrival detection, completes assignments.
    """
    from backend.services.arrival_detection import detect_arrival

    db = SessionLocal()
    try:
        for truck_id in truck_ids:
            assignment = db.query(Assignment).filter(
                Assignment.truck_id == truck_id,
                Assignment.status == "in_transit",
            ).first()

            if not assignment:
                continue

            truck = db.query(Truck).filter(
                Truck.truck_id == truck_id
            ).first()

            shipment = db.query(Shipment).filter(
                Shipment.load_id == assignment.load_id
            ).first()

            if not truck or not shipment:
                continue

            if (
                truck.current_latitude is None
                or truck.current_longitude is None
                or shipment.pickup_latitude is None
                or shipment.destination_latitude is None
            ):
                continue

            start_lat = truck.current_latitude
            start_lon = truck.current_longitude
            pickup_lat = shipment.pickup_latitude
            pickup_lon = shipment.pickup_longitude
            dest_lat = shipment.destination_latitude
            dest_lon = shipment.destination_longitude

            # Stage 1: current -> pickup
            for step in range(STEPS + 1):
                t = step / STEPS
                lat = start_lat + (pickup_lat - start_lat) * t
                lon = start_lon + (pickup_lon - start_lon) * t
                speed = 0 if step == STEPS else 60
                _write_location(db, truck, lat, lon, speed)
                if step < STEPS:
                    time.sleep(INTERVAL_SECONDS)

            # Stage 2: pickup -> destination
            for step in range(STEPS + 1):
                t = step / STEPS
                lat = pickup_lat + (dest_lat - pickup_lat) * t
                lon = pickup_lon + (dest_lon - pickup_lon) * t
                speed = 0 if step == STEPS else 60
                _write_location(db, truck, lat, lon, speed)
                if step < STEPS:
                    time.sleep(INTERVAL_SECONDS)

            # Arrival detection + completion
            try:
                arrival = detect_arrival(db, assignment.assignment_id)
                if arrival.get("arrived"):
                    from backend.api.assignments import complete_assignment
                    complete_assignment(assignment.assignment_id, db)
            except Exception as exc:
                print(f"[simulator] arrival check failed for truck {truck_id}: {exc}")

    finally:
        db.close()


# -------------------------------------------------
# Endpoints
# -------------------------------------------------

@router.post("/run")
def run_simulation(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Start server-side simulation for all in_transit trucks.
    Returns immediately; movement happens in the background.
    """
    active = db.query(Assignment).filter(
        Assignment.status == "in_transit"
    ).all()

    if not active:
        return {
            "status": "no_active_assignments",
            "message": (
                "No trucks are currently in transit. "
                "Assign & Start a trip first."
            ),
            "trucks": [],
        }

    truck_ids = [a.truck_id for a in active]

    background_tasks.add_task(_run_full_simulation, truck_ids)

    return {
        "status": "started",
        "message": f"Simulating {len(truck_ids)} truck(s) in transit.",
        "trucks": truck_ids,
        "expected_duration_seconds": len(truck_ids) * STEPS * 2 * INTERVAL_SECONDS,
    }


@router.get("/status")
def simulation_status(
    db: Session = Depends(get_db),
):
    """Return current in_transit count (frontend polls this)."""
    in_transit = db.query(Assignment).filter(
        Assignment.status == "in_transit"
    ).count()

    return {
        "in_transit": in_transit,
        "running": in_transit > 0,
    }
