from backend.models.truck import Truck
from backend.models.shipment import Shipment
from backend.models.truck_location import TruckLocation

from backend.services.backhaul_matching import calculate_distance


def find_baseline_match(
    truck_id: int,
    db
):
    """
    Baseline backhaul matching strategy.

    Strategy:
    1. Find the truck.
    2. Get its latest location.
    3. Find available shipments.
    4. Apply basic feasibility constraints.
    5. Select the shipment with the minimum
       distance to pickup.

    The baseline intentionally does NOT use:
    - ML
    - optimization
    - revenue scoring
    - profit scoring
    - route efficiency
    - recommendation scoring
    """

    # -------------------------------------------------
    # 1. Find truck
    # -------------------------------------------------

    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        return {
            "truck_id": truck_id,
            "matched": False,
            "message": "Truck not found"
        }

    # -------------------------------------------------
    # 2. Get latest truck location
    # -------------------------------------------------

    latest_location = db.query(TruckLocation).filter(
        TruckLocation.truck_id == truck_id
    ).order_by(
        TruckLocation.timestamp.desc()
    ).first()

    if not latest_location:
        return {
            "truck_id": truck_id,
            "matched": False,
            "message": "No location data available"
        }

    # -------------------------------------------------
    # 3. Calculate remaining capacity
    # -------------------------------------------------

    remaining_capacity = (
        truck.capacity - truck.current_load
    )

    # -------------------------------------------------
    # 4. Get available shipments
    # -------------------------------------------------

    shipments = db.query(Shipment).filter(
        Shipment.status == "available"
    ).all()

    if not shipments:
        return {
            "truck_id": truck_id,
            "matched": False,
            "message": "No available shipments"
        }

    feasible_shipments = []

    # -------------------------------------------------
    # 5. Evaluate basic feasibility
    # -------------------------------------------------

    for shipment in shipments:

        # Pickup coordinates required
        if (
            shipment.pickup_latitude is None
            or shipment.pickup_longitude is None
        ):
            continue

        # Capacity constraint
        if shipment.weight > remaining_capacity:
            continue

        # Calculate pickup distance
        distance_to_pickup = calculate_distance(
            latest_location.latitude,
            latest_location.longitude,
            shipment.pickup_latitude,
            shipment.pickup_longitude
        )

        feasible_shipments.append({
            "load_id": shipment.load_id,
            "pickup_city": shipment.pickup_city,
            "destination_city": shipment.destination_city,
            "weight": shipment.weight,
            "cargo_type": shipment.cargo_type,
            "revenue": shipment.revenue,
            "distance_to_pickup_km": round(
                distance_to_pickup,
                2
            )
        })

    # -------------------------------------------------
    # 6. No feasible shipment
    # -------------------------------------------------

    if not feasible_shipments:
        return {
            "truck_id": truck_id,
            "matched": False,
            "remaining_capacity": remaining_capacity,
            "message": "No feasible shipment found"
        }

    # -------------------------------------------------
    # 7. Select nearest shipment
    # -------------------------------------------------

    feasible_shipments.sort(
        key=lambda x: x["distance_to_pickup_km"]
    )

    selected = feasible_shipments[0]

    # -------------------------------------------------
    # 8. Return baseline decision
    # -------------------------------------------------

    return {
        "truck_id": truck_id,

        "strategy": "Nearest Compatible Shipment",

        "matched": True,

        "remaining_capacity": remaining_capacity,

        "selected_load": selected,

        "candidate_count": len(
            feasible_shipments
        )
    }