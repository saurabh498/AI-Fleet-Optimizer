from sqlalchemy.orm import Session

from backend.models.assignment import Assignment
from backend.models.shipment import Shipment
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation
from backend.services.route_optimizer import calculate_distance_km


ARRIVAL_THRESHOLD_KM = 1.0


def detect_arrival(
    db: Session,
    assignment_id: int
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        return {
            "arrived": False,
            "message": "Assignment not found"
        }

    if assignment.status != "in_transit":
        return {
            "arrived": False,
            "message": f"Assignment is {assignment.status}, not in_transit"
        }

    truck = db.query(Truck).filter(
        Truck.truck_id == assignment.truck_id
    ).first()

    shipment = db.query(Shipment).filter(
        Shipment.load_id == assignment.load_id
    ).first()

    if not truck or not shipment:
        return {
            "arrived": False,
            "message": "Truck or shipment not found"
        }

    latest_location = db.query(TruckLocation).filter(
        TruckLocation.truck_id == truck.truck_id
    ).order_by(
        TruckLocation.timestamp.desc()
    ).first()

    if not latest_location:
        return {
            "arrived": False,
            "message": "No GPS location available"
        }

    distance = calculate_distance_km(
        latest_location.latitude,
        latest_location.longitude,
        shipment.destination_latitude,
        shipment.destination_longitude
    )

    arrived = distance <= ARRIVAL_THRESHOLD_KM

    return {
        "arrived": arrived,
        "assignment_id": assignment.assignment_id,
        "truck_id": truck.truck_id,
        "load_id": shipment.load_id,
        "current_latitude": latest_location.latitude,
        "current_longitude": latest_location.longitude,
        "destination_latitude": shipment.destination_latitude,
        "destination_longitude": shipment.destination_longitude,
        "distance_to_destination_km": distance,
        "arrival_threshold_km": ARRIVAL_THRESHOLD_KM,
        "message": (
            "Truck has arrived at destination"
            if arrived
            else "Truck is still in transit"
        )
    }