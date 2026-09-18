from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.api.deps import get_current_user, require_role
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation
from backend.schemas.truck import TruckCreate, TruckResponse


router = APIRouter(
    prefix="/trucks",
    tags=["Trucks"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    response_model=TruckResponse,
    dependencies=[Depends(require_role("manager", "admin"))],
)
def create_truck(
    truck_data: TruckCreate,
    db: Session = Depends(get_db)
):
    truck = Truck(**truck_data.model_dump())

    db.add(truck)
    db.flush()

    if (
        truck.current_latitude is not None
        and truck.current_longitude is not None
    ):
        db.add(
            TruckLocation(
                truck_id=truck.truck_id,
                timestamp=datetime.now(),
                latitude=truck.current_latitude,
                longitude=truck.current_longitude,
                speed=0
            )
        )

    db.commit()
    db.refresh(truck)

    return truck


@router.get("/", response_model=list[TruckResponse])
def get_trucks(
    db: Session = Depends(get_db)
):
    return db.query(Truck).all()


@router.get("/{truck_id}", response_model=TruckResponse)
def get_truck(
    truck_id: int,
    db: Session = Depends(get_db)
):
    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    return truck


@router.put(
    "/{truck_id}",
    response_model=TruckResponse,
    dependencies=[Depends(require_role("manager", "admin"))],
)
def update_truck(
    truck_id: int,
    truck_data: TruckCreate,
    db: Session = Depends(get_db)
):
    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    for key, value in truck_data.model_dump().items():
        setattr(truck, key, value)

    db.commit()
    db.refresh(truck)

    return truck


@router.delete(
    "/{truck_id}",
    dependencies=[Depends(require_role("manager", "admin"))],
)
def delete_truck(
    truck_id: int,
    db: Session = Depends(get_db)
):
    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    db.delete(truck)
    db.commit()

    return {
        "message": "Truck deleted successfully",
        "truck_id": truck_id
    }
