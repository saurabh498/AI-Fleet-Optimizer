from backend.models.truck import Truck
from backend.models.shipment import Shipment
from backend.models.assignment import Assignment
from backend.models.assignment_history import AssignmentHistory


def execute_fleet_assignments(db, recommendations):
    """
    Execute optimized fleet assignments.

    Each selected truck-load pair is validated again
    before creating the actual assignment.
    """

    executed = []
    rejected = []

    for recommendation in recommendations:

        truck_id = recommendation["truck_id"]
        load_id = recommendation["load_id"]

        # ---------------------------------------------
        # Find truck
        # ---------------------------------------------
        truck = db.query(Truck).filter(
            Truck.truck_id == truck_id
        ).first()

        if truck is None:
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Truck not found"
            })
            continue

        # ---------------------------------------------
        # Find shipment
        # ---------------------------------------------
        shipment = db.query(Shipment).filter(
            Shipment.load_id == load_id
        ).first()

        if shipment is None:
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Shipment not found"
            })
            continue

        # ---------------------------------------------
        # Availability validation
        # ---------------------------------------------
        if truck.status != "available":
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Truck is not available"
            })
            continue

        if shipment.status != "available":
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Shipment is not available"
            })
            continue

        # ---------------------------------------------
        # Capacity validation
        # ---------------------------------------------
        current_load = truck.current_load or 0
        remaining_capacity = truck.capacity - current_load

        if shipment.weight > remaining_capacity:
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Shipment exceeds remaining capacity"
            })
            continue

        # ---------------------------------------------
        # Duplicate truck assignment protection
        # ---------------------------------------------
        active_truck_assignment = db.query(
            Assignment
        ).filter(
            Assignment.truck_id == truck_id,
            Assignment.status.in_([
                "assigned",
                "in_transit"
            ])
        ).first()

        if active_truck_assignment:
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Truck already has an active assignment"
            })
            continue

        # ---------------------------------------------
        # Duplicate shipment assignment protection
        # ---------------------------------------------
        active_shipment_assignment = db.query(
            Assignment
        ).filter(
            Assignment.load_id == load_id,
            Assignment.status.in_([
                "assigned",
                "in_transit"
            ])
        ).first()

        if active_shipment_assignment:
            rejected.append({
                "truck_id": truck_id,
                "load_id": load_id,
                "reason": "Shipment already has an active assignment"
            })
            continue

        # ---------------------------------------------
        # Create assignment
        # ---------------------------------------------
        assignment = Assignment(
            truck_id=truck_id,
            load_id=load_id,
            match_score=recommendation.get(
                "match_score", 0
            ),
            estimated_distance=recommendation.get(
                "estimated_distance",
                0
            ),
            estimated_cost=recommendation.get(
                "estimated_route_cost",
                0
            ),
            estimated_profit=recommendation.get(
                "estimated_route_profit",
                0
            ),
            recommendation=recommendation.get(
                "recommendation",
                "Recommended"
            ),
            status="assigned"
        )

        db.add(assignment)
        db.flush()

        # ---------------------------------------------
        # Assignment history
        # ---------------------------------------------
        history = AssignmentHistory(
            assignment_id=assignment.assignment_id,
            status="assigned"
        )

        db.add(history)

        # ---------------------------------------------
        # Update truck
        # ---------------------------------------------
        truck.status = "assigned"
        truck.current_load = (
            current_load + shipment.weight
        )
        truck.destination = shipment.destination_city

        # ---------------------------------------------
        # Update shipment
        # ---------------------------------------------
        shipment.status = "assigned"

        executed.append({
            "assignment_id": assignment.assignment_id,
            "truck_id": truck_id,
            "load_id": load_id,
            "status": "assigned",
            "optimization_score": recommendation.get(
                "optimization_score",
                0
            )
        })

    db.commit()

    return {
        "message": "Fleet assignments executed",
        "total_requested": len(recommendations),
        "total_executed": len(executed),
        "total_rejected": len(rejected),
        "executed_assignments": executed,
        "rejected_assignments": rejected
    }