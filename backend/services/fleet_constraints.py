from backend.models.truck import Truck
from backend.models.shipment import Shipment
from backend.models.assignment import Assignment
from backend.models.truck_location import TruckLocation


ACTIVE_ASSIGNMENT_STATUSES = [
    "assigned",
    "in_transit"
]


def validate_fleet_candidate(
    db,
    truck: Truck,
    shipment: Shipment
):
    """
    Validate whether a truck-shipment pair is
    feasible for fleet-level recommendation.

    Returns:
        {
            "feasible": True/False,
            "reasons": [...]
        }
    """

    reasons = []

    # -------------------------------------------------
    # 1. Truck availability
    # -------------------------------------------------
    if truck.status != "available":
        reasons.append(
            "Truck is not available"
        )

    # -------------------------------------------------
    # 2. Shipment availability
    # -------------------------------------------------
    if shipment.status != "available":
        reasons.append(
            "Shipment is not available"
        )

    # -------------------------------------------------
    # 3. Capacity constraint
    # -------------------------------------------------
    if shipment.weight is None:
        reasons.append(
            "Shipment weight is missing"
        )
    elif truck.capacity is None:
        reasons.append(
            "Truck capacity is missing"
        )
    else:
        current_load = truck.current_load or 0
        remaining_capacity = truck.capacity - current_load

        if shipment.weight > remaining_capacity:
            reasons.append(
                "Shipment exceeds truck remaining capacity"
            )

    # -------------------------------------------------
    # 4. Check active truck assignments
    # -------------------------------------------------
    truck_active_assignment = db.query(Assignment).filter(
        Assignment.truck_id == truck.truck_id,
        Assignment.status.in_(ACTIVE_ASSIGNMENT_STATUSES)
    ).first()

    if truck_active_assignment:
        reasons.append(
            "Truck already has an active assignment"
        )

    # -------------------------------------------------
    # 5. Check active shipment assignments
    # -------------------------------------------------
    shipment_active_assignment = db.query(Assignment).filter(
        Assignment.load_id == shipment.load_id,
        Assignment.status.in_(ACTIVE_ASSIGNMENT_STATUSES)
    ).first()

    if shipment_active_assignment:
        reasons.append(
            "Shipment already has an active assignment"
        )

    # -------------------------------------------------
    # 6. Truck current location
    # -------------------------------------------------
    if (
        truck.current_latitude is None
        or truck.current_longitude is None
    ):
        reasons.append(
            "Truck current location is missing"
        )

    # -------------------------------------------------
    # 7. Shipment pickup coordinates
    # -------------------------------------------------
    if (
        shipment.pickup_latitude is None
        or shipment.pickup_longitude is None
    ):
        reasons.append(
            "Shipment pickup coordinates are missing"
        )

    # -------------------------------------------------
    # 8. Shipment destination coordinates
    # -------------------------------------------------
    if (
        shipment.destination_latitude is None
        or shipment.destination_longitude is None
    ):
        reasons.append(
            "Shipment destination coordinates are missing"
        )

    # -------------------------------------------------
    # 9. Latest GPS location record
    # -------------------------------------------------
    latest_location = db.query(TruckLocation).filter(
        TruckLocation.truck_id == truck.truck_id
    ).order_by(
        TruckLocation.timestamp.desc()
    ).first()

    if latest_location is None:
        reasons.append(
            "Latest truck GPS location is missing"
        )

    # -------------------------------------------------
    # Final feasibility result
    # -------------------------------------------------
    return {
        "feasible": len(reasons) == 0,
        "reasons": reasons
    }