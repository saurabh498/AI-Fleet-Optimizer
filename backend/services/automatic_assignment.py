from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.assignment import Assignment
from backend.models.shipment import Shipment
from backend.models.truck import Truck
from backend.models.assignment_history import AssignmentHistory
from backend.services.assignment_decision import generate_assignment_decision


def execute_best_assignment(
    truck_id: int,
    db: Session
):
    """
    Automatically execute the best backhaul assignment
    when the decision layer returns ASSIGN_NOW.
    """

    # -------------------------------------------------
    # 1. Find truck
    # -------------------------------------------------

    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    # -------------------------------------------------
    # 2. Validate truck availability
    # -------------------------------------------------

    if truck.status != "available":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Truck is not available. "
                f"Current status: {truck.status}"
            )
        )

    # -------------------------------------------------
    # 3. Generate best assignment decision
    # -------------------------------------------------

    decision = generate_assignment_decision(
        truck_id,
        db
    )

    if decision is None:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    # -------------------------------------------------
    # 4. Check decision
    # -------------------------------------------------

    if decision["decision"] != "ASSIGN_NOW":
        return {
            "truck_id": truck_id,
            "executed": False,
            "decision": decision["decision"],
            "message": (
                "Automatic assignment was not executed"
            ),
            "reason": decision["reason"],
            "waiting_recommendation": decision.get(
                "waiting_recommendation"
            )
        }

    best_match = decision["best_match"]

    load_id = best_match["load_id"]

    # -------------------------------------------------
    # 5. Find shipment
    # -------------------------------------------------

    shipment = db.query(Shipment).filter(
        Shipment.load_id == load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Selected shipment not found"
        )

    # -------------------------------------------------
    # 6. Validate shipment availability
    # -------------------------------------------------

    if shipment.status != "available":
        raise HTTPException(
            status_code=400,
            detail=(
                "Selected shipment is no longer available"
            )
        )

    # -------------------------------------------------
    # 7. Duplicate assignment protection
    # -------------------------------------------------

    existing_assignment = db.query(
        Assignment
    ).filter(
        Assignment.load_id == load_id,
        Assignment.status.in_([
            "assigned",
            "in_transit"
        ])
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail=(
                "Shipment is already assigned "
                "to an active assignment"
            )
        )

    # -------------------------------------------------
    # 8. Capacity validation
    # -------------------------------------------------

    remaining_capacity = (
        truck.capacity - truck.current_load
    )

    if shipment.weight > remaining_capacity:
        raise HTTPException(
            status_code=400,
            detail=(
                "Shipment exceeds truck remaining capacity"
            )
        )

    # -------------------------------------------------
    # 9. Create assignment
    # -------------------------------------------------

    assignment = Assignment(
        truck_id=truck.truck_id,
        load_id=shipment.load_id,
        match_score=best_match["match_score"],
        estimated_distance=best_match[
            "route"
        ]["total_distance_km"],
        estimated_cost=best_match[
            "estimated_route_cost"
        ],
        estimated_profit=best_match[
            "estimated_route_profit"
        ],
        waiting_time=0,
        recommendation=best_match[
            "recommendation"
        ],
    )

    db.add(assignment)

    # Generate assignment ID
    db.flush()

    # -------------------------------------------------
    # 10. Assignment history
    # -------------------------------------------------

    history = AssignmentHistory(
        assignment_id=assignment.assignment_id,
        status="assigned"
    )

    db.add(history)

    # -------------------------------------------------
    # 11. Update truck state
    # -------------------------------------------------

    truck.current_load = (
        truck.current_load + shipment.weight
    )

    truck.status = "assigned"

    truck.destination = shipment.destination_city

    # -------------------------------------------------
    # 12. Update shipment state
    # -------------------------------------------------

    shipment.status = "assigned"

    db.commit()

    db.refresh(assignment)
    db.refresh(truck)
    db.refresh(shipment)

    # -------------------------------------------------
    # 13. Return execution result
    # -------------------------------------------------

    return {
        "truck_id": truck.truck_id,

        "executed": True,

        "decision": "ASSIGN_NOW",

        "message": (
            "Best backhaul shipment "
            "automatically assigned successfully"
        ),

        "assignment": {
            "assignment_id": assignment.assignment_id,
            "truck_id": assignment.truck_id,
            "load_id": assignment.load_id,
            "status": assignment.status,
            "match_score": assignment.match_score,
            "estimated_distance": assignment.estimated_distance,
            "estimated_cost": assignment.estimated_cost,
            "estimated_profit": assignment.estimated_profit
        },

        "truck": {
            "truck_id": truck.truck_id,
            "status": truck.status,
            "current_load": truck.current_load,
            "destination": truck.destination
        },

        "shipment": {
            "load_id": shipment.load_id,
            "status": shipment.status
        }
    }