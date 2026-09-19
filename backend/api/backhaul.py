from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.models.truck import Truck
from backend.models.shipment import Shipment

from backend.services.backhaul_matching import find_backhaul_matches

from backend.services.best_backhaul import (
    select_best_backhaul
)

from backend.services.assignment_decision import (
    generate_assignment_decision
)

from backend.services.automatic_assignment import (
    execute_best_assignment
)

from backend.services.fleet_optimizer import optimize_fleet

from backend.services.fleet_assignment_executor import execute_fleet_assignments

from backend.services.reoptimization import reoptimize_fleet

from backend.services.baseline_vs_ai import compare_baseline_vs_ai



from backend.services.route_optimizer import (
    calculate_route_distances,
    calculate_route_efficiency
)
from backend.api.deps import get_current_user

router = APIRouter(
    prefix="/backhaul",
    tags=["Backhaul Matching"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/match/{truck_id}")
def get_backhaul_matches(
    truck_id: int,
    db: Session = Depends(get_db)
):
    result = find_backhaul_matches(
        truck_id,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    return result

@router.get("/route/{truck_id}/{load_id}")
def optimize_route(
    truck_id: int,
    load_id: int,
    db: Session = Depends(get_db)
):
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
    # 2. Find shipment
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
    # 3. Validate truck coordinates
    # -------------------------------------------------

    if (
        truck.current_latitude is None
        or truck.current_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Truck location is not available"
        )

    # -------------------------------------------------
    # 4. Validate shipment pickup coordinates
    # -------------------------------------------------

    if (
        shipment.pickup_latitude is None
        or shipment.pickup_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Shipment pickup location is not available"
        )

    # -------------------------------------------------
    # 5. Validate shipment destination coordinates
    # -------------------------------------------------

    if (
        shipment.destination_latitude is None
        or shipment.destination_longitude is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Shipment destination location is not available"
        )

    # -------------------------------------------------
    # 6. Calculate route distances
    # -------------------------------------------------

    route = calculate_route_distances(
        truck_latitude=truck.current_latitude,
        truck_longitude=truck.current_longitude,
        pickup_latitude=shipment.pickup_latitude,
        pickup_longitude=shipment.pickup_longitude,
        destination_latitude=shipment.destination_latitude,
        destination_longitude=shipment.destination_longitude,
        truck_type=truck.truck_type,
        db=db
    )

    # -------------------------------------------------
    # 7. Calculate route efficiency
    # -------------------------------------------------

    efficiency = calculate_route_efficiency(
        revenue=shipment.revenue,
        total_distance_km=route["total_distance_km"],
        estimated_cost=route["estimated_cost"]
    )

    # -------------------------------------------------
    # 8. Return optimization result
    # -------------------------------------------------

    return {
        "truck": {
            "truck_id": truck.truck_id,
            "current_city": truck.current_city,
            "current_latitude": truck.current_latitude,
            "current_longitude": truck.current_longitude,
            "cost_per_km": truck.cost_per_km
        },

        "shipment": {
            "load_id": shipment.load_id,
            "pickup_city": shipment.pickup_city,
            "destination_city": shipment.destination_city,
            "revenue": shipment.revenue
        },

        "route": route,

        "efficiency": efficiency
    }

@router.get("/best/{truck_id}")
def get_best_backhaul(
    truck_id: int,
    db: Session = Depends(get_db)
):
    result = select_best_backhaul(
        truck_id,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    return result

@router.get("/decision/{truck_id}")
def get_assignment_decision(
    truck_id: int,
    db: Session = Depends(get_db)
):
    result = generate_assignment_decision(
        truck_id,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    return result

@router.post("/auto-assign/{truck_id}")
def auto_assign_best_backhaul(
    truck_id: int,
    db: Session = Depends(get_db)
):
    return execute_best_assignment(
        truck_id,
        db
    )

@router.get("/fleet-optimize")
def fleet_optimization(
    db: Session = Depends(get_db)
):
    return optimize_fleet(db)

@router.post("/fleet-execute")
def fleet_execute(
    db: Session = Depends(get_db)
):
    optimization = optimize_fleet(db)

    recommendations = optimization.get(
        "assignments",
        []
    )

    if not recommendations:
        return {
            "message": "No fleet assignments available for execution",
            "total_requested": 0,
            "total_executed": 0,
            "total_rejected": 0,
            "executed_assignments": [],
            "rejected_assignments": []
        }

    return execute_fleet_assignments(
        db,
        recommendations
    )

@router.get("/fleet-reoptimize")
def fleet_reoptimize(db: Session = Depends(get_db)):
    return reoptimize_fleet(db)

@router.get("/baseline-vs-ai/{truck_id}")
def baseline_vs_ai_comparison(
    truck_id: int,
    db: Session = Depends(get_db)
):
    result = compare_baseline_vs_ai(
        truck_id,
        db
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    if result.get("message") == "Truck not found":
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    return result