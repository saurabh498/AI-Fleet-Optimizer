from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.assignment import Assignment
from backend.models.shipment import Shipment
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation
from backend.services.backhaul_matching import find_backhaul_matches
from backend.models.assignment_history import AssignmentHistory
from backend.services.reoptimization import reoptimize_fleet
from backend.services.fleet_assignment_executor import execute_fleet_assignments
from backend.services.arrival_detection import detect_arrival

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)

@router.post("/truck/{truck_id}/load/{load_id}")
def assign_shipment(
    truck_id: int,
    load_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Check truck
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
    # 2. Check shipment
    # -------------------------------------------------

    shipment = db.query(Shipment).filter(
        Shipment.load_id == load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    # -------------------------------------------------
    # 3. Check shipment availability
    # -------------------------------------------------

    if shipment.status != "available":
        raise HTTPException(
            status_code=400,
            detail="Shipment is not available for assignment"
        )

    # -------------------------------------------------
    # 4. Get matching recommendations
    # -------------------------------------------------

    matching_result = find_backhaul_matches(
        truck_id,
        db
    )

    if matching_result is None:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    matches = matching_result.get(
        "matches",
        []
    )

    # -------------------------------------------------
    # 5. Find requested shipment in matches
    # -------------------------------------------------

    selected_match = None

    for match in matches:

        if match["load_id"] == load_id:
            selected_match = match
            break

    if selected_match is None:
        raise HTTPException(
            status_code=400,
            detail="Shipment is not a suitable backhaul match for this truck"
        )

    # -------------------------------------------------
    # 6. Check duplicate assignment
    # -------------------------------------------------

    existing_assignment = db.query(Assignment).filter(
        Assignment.truck_id == truck_id,
        Assignment.load_id == load_id
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=400,
            detail="Shipment is already assigned to this truck"
        )

    # -------------------------------------------------
    # 7. Create assignment
    # -------------------------------------------------

    assignment = Assignment(
        truck_id=truck_id,
        load_id=load_id,
        match_score=selected_match["match_score"],
        estimated_distance=selected_match["distance_to_pickup_km"],
        estimated_cost=selected_match["estimated_pickup_cost"],
        estimated_profit=selected_match["estimated_net_revenue"],
        waiting_time=0,
        recommendation=selected_match["recommendation"],
        created_at=datetime.utcnow()
    )

    db.add(assignment)

    # Generate assignment_id before creating history
    db.flush()

    # -------------------------------------------------
    # 8. Record assignment history
    # -------------------------------------------------

    assignment_history = AssignmentHistory(
        assignment_id=assignment.assignment_id,
        status="assigned",
        changed_at=datetime.utcnow()
    )

    db.add(assignment_history)

    # -------------------------------------------------
    # 9. Update shipment and truck status
    # -------------------------------------------------

    truck.current_load = shipment.weight
    truck.status = "assigned"
    truck.destination = shipment.destination_city

    shipment.status = "assigned"

    # -------------------------------------------------
    # 10. Commit
    # -------------------------------------------------

    db.commit()
    db.refresh(assignment)

    # -------------------------------------------------
    # 11. Return assignment details
    # -------------------------------------------------

    return {
        "message": "Shipment assigned successfully",

        "assignment": {
            "assignment_id": assignment.assignment_id,
            "truck_id": assignment.truck_id,
            "load_id": assignment.load_id,
            "match_score": assignment.match_score,
            "estimated_distance": assignment.estimated_distance,
            "estimated_cost": assignment.estimated_cost,
            "estimated_profit": assignment.estimated_profit,
            "waiting_time": assignment.waiting_time,
            "recommendation": assignment.recommendation,
            "created_at": assignment.created_at
        }
    }

@router.get("/")
def get_assignments(
    db: Session = Depends(get_db)
):
    assignments = db.query(Assignment).all()

    return assignments


@router.get("/{assignment_id}/history")
def get_assignment_history(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Check assignment
    # -------------------------------------------------

    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    # -------------------------------------------------
    # 2. Get assignment history
    # -------------------------------------------------

    history = db.query(AssignmentHistory).filter(
        AssignmentHistory.assignment_id == assignment_id
    ).order_by(
        AssignmentHistory.changed_at.asc()
    ).all()

    # -------------------------------------------------
    # 3. Return history
    # -------------------------------------------------

    return {
        "assignment_id": assignment_id,
        "history": [
            {
                "history_id": item.history_id,
                "status": item.status,
                "changed_at": item.changed_at
            }
            for item in history
        ]
    }


@router.get("/{assignment_id}/details")
def get_assignment_details(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    truck = db.query(Truck).filter(
        Truck.truck_id == assignment.truck_id
    ).first()

    shipment = db.query(Shipment).filter(
        Shipment.load_id == assignment.load_id
    ).first()

    return {
        "assignment": {
            "assignment_id": assignment.assignment_id,
            "truck_id": assignment.truck_id,
            "load_id": assignment.load_id,
            "match_score": assignment.match_score,
            "estimated_distance": assignment.estimated_distance,
            "estimated_cost": assignment.estimated_cost,
            "estimated_profit": assignment.estimated_profit,
            "waiting_time": assignment.waiting_time,
            "recommendation": assignment.recommendation,
            "status": assignment.status,
            "created_at": assignment.created_at
        },

        "truck": {
            "truck_id": truck.truck_id,
            "truck_type": truck.truck_type,
            "capacity": truck.capacity,
            "current_load": truck.current_load,
            "status": truck.status,
            "destination": truck.destination
        },

        "shipment": {
            "load_id": shipment.load_id,
            "pickup_city": shipment.pickup_city,
            "destination_city": shipment.destination_city,
            "weight": shipment.weight,
            "cargo_type": shipment.cargo_type,
            "revenue": shipment.revenue,
            "status": shipment.status
        }
    }

@router.get("/{assignment_id}")
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    return assignment


@router.put("/{assignment_id}/start")
def start_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    # 1. Find assignment
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    # 2. Validate assignment status
    if assignment.status == "in_transit":
        raise HTTPException(
            status_code=400,
            detail="Assignment is already in transit"
        )

    if assignment.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Completed assignment cannot be started"
        )

    if assignment.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled assignment cannot be started"
        )

    if assignment.status != "assigned":
        raise HTTPException(
            status_code=400,
            detail="Only assigned assignments can be started"
        )

    # 3. Find truck
    truck = db.query(Truck).filter(
        Truck.truck_id == assignment.truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    # 4. Find shipment
    shipment = db.query(Shipment).filter(
        Shipment.load_id == assignment.load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    # 5. Validate shipment status
    if shipment.status != "assigned":
        raise HTTPException(
            status_code=400,
            detail="Shipment must be assigned before starting"
        )

    # 6. Validate truck status
    if truck.status != "assigned":
        raise HTTPException(
            status_code=400,
            detail="Truck must be assigned before starting"
        )

    # 7. Start assignment
    assignment.status = "in_transit"

    # 8. Update truck state
    truck.status = "in_transit"
    truck.current_load = shipment.weight
    truck.destination = shipment.destination_city

    # 9. Update shipment state
    shipment.status = "in_transit"

    # 10. Record truck location
    if (
    truck.current_latitude is not None
    and truck.current_longitude is not None
    ):
        location = TruckLocation(
            truck_id=truck.truck_id,
            timestamp=datetime.utcnow(),
            latitude=truck.current_latitude,
            longitude=truck.current_longitude,
            speed=None
        )
        db.add(location)


    # -------------------------------------------------
    # 11. Record assignment history
    # -------------------------------------------------

    assignment_history = AssignmentHistory(
        assignment_id=assignment.assignment_id,
        status="in_transit",
        changed_at=datetime.utcnow()
    )

    db.add(assignment_history)
       
    # 12. Commit changes
    db.commit()

    db.refresh(assignment)
    db.refresh(truck)
    db.refresh(shipment)

    # 13. Return updated state
    return {
        "message": "Assignment started successfully",

        "assignment": {
            "assignment_id": assignment.assignment_id,
            "truck_id": assignment.truck_id,
            "load_id": assignment.load_id,
            "status": assignment.status
        },

        "truck": {
            "truck_id": truck.truck_id,
            "current_load": truck.current_load,
            "status": truck.status,
            "destination": truck.destination
        },

        "shipment": {
            "load_id": shipment.load_id,
            "status": shipment.status
        }
    }


@router.put("/{assignment_id}/complete")
def complete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Find assignment
    # -------------------------------------------------

    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    # -------------------------------------------------
    # 2. Validate assignment status
    # -------------------------------------------------

    if assignment.status == "completed":
        raise HTTPException(
            status_code=400,
            detail="Assignment is already completed"
        )

    if assignment.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled assignment cannot be completed"
        )

    if assignment.status != "in_transit":
        raise HTTPException(
            status_code=400,
            detail="Assignment must be in transit before completion"
        )

    # -------------------------------------------------
    # 3. Find truck
    # -------------------------------------------------

    truck = db.query(Truck).filter(
        Truck.truck_id == assignment.truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    # -------------------------------------------------
    # 4. Find shipment
    # -------------------------------------------------

    shipment = db.query(Shipment).filter(
        Shipment.load_id == assignment.load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    # -------------------------------------------------
    # 5. Complete assignment
    # -------------------------------------------------

    assignment.status = "completed"

    # -------------------------------------------------
    # 6. Complete shipment
    # -------------------------------------------------

    shipment.status = "delivered"

    # -------------------------------------------------
    # 7. Make truck available
    # -------------------------------------------------

    truck.current_load = 0
    truck.status = "available"
    truck.destination = None

    # -------------------------------------------------
    # 8. Record assignment history
    # -------------------------------------------------

    assignment_history = AssignmentHistory(
        assignment_id=assignment.assignment_id,
        status="completed",
        changed_at=datetime.utcnow()
    )

    db.add(assignment_history)

    # -------------------------------------------------
    # 9. Commit completed assignment state
    # -------------------------------------------------

    db.commit()

    db.refresh(assignment)
    db.refresh(truck)
    db.refresh(shipment)

    # -------------------------------------------------
    # 10. Re-optimize fleet after completion
    # -------------------------------------------------

    reoptimization = reoptimize_fleet(db)

    # -------------------------------------------------
    # 11. Automatically execute new recommendations
    # -------------------------------------------------

    optimization_data = reoptimization.get(
        "optimization",
        {}
    )

    recommendations = optimization_data.get(
        "assignments",
        []
    )

    if recommendations:
        automatic_execution = execute_fleet_assignments(
            db,
            recommendations
        )
    else:
        automatic_execution = {
            "message": "No new fleet assignments to execute",
            "total_requested": 0,
            "total_executed": 0,
            "total_rejected": 0,
            "executed_assignments": [],
            "rejected_assignments": []
        }

    # -------------------------------------------------
    # 12. Refresh state after automatic assignment
    # -------------------------------------------------

    db.refresh(assignment)
    db.refresh(truck)
    db.refresh(shipment)

    # -------------------------------------------------
    # 13. Return completion + reoptimization + execution
    # -------------------------------------------------

    return {
        "message": "Assignment completed successfully",

        "assignment": {
        "assignment_id": assignment.assignment_id,
        "truck_id": assignment.truck_id,
        "load_id": assignment.load_id,
        "status": assignment.status
        },

        "truck": {
        "truck_id": truck.truck_id,
        "current_load": truck.current_load,
        "status": truck.status,
        "destination": truck.destination
        },

        "shipment": {
        "load_id": shipment.load_id,
        "status": shipment.status
        },

        "reoptimization": reoptimization,

        "automatic_execution": automatic_execution
    }

@router.get("/{assignment_id}/arrival")
def check_assignment_arrival(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    # -------------------------------------------------
    # 1. Detect arrival
    # -------------------------------------------------

    arrival_result = detect_arrival(
        db,
        assignment_id
    )

    # -------------------------------------------------
    # 2. If truck has not arrived
    # -------------------------------------------------

    if not arrival_result.get("arrived", False):
        return arrival_result

    # -------------------------------------------------
    # 3. Automatically complete assignment
    # -------------------------------------------------

    completion_result = complete_assignment(
        assignment_id,
        db
    )

    # -------------------------------------------------
    # 4. Return arrival + completion result
    # -------------------------------------------------

    return {
        "message": "Truck arrived and assignment completed automatically",
        "arrival": arrival_result,
        "completion": completion_result
    }  