from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.truck_location import TruckLocation
from backend.schemas.truck_location import (
    TruckLocationCreate,
    TruckLocationResponse
)


router = APIRouter(
    prefix="/locations",
    tags=["Truck Locations"]
)


@router.post("/", response_model=TruckLocationResponse)
def create_location(
    location_data: TruckLocationCreate,
    db: Session = Depends(get_db)
):
    location = TruckLocation(**location_data.model_dump())

    db.add(location)
    db.commit()
    db.refresh(location)

    return location

@router.get("/", response_model=list[TruckLocationResponse])
def get_locations(
    db: Session = Depends(get_db)
):
    return db.query(TruckLocation).all()

@router.get("/truck/{truck_id}/latest", response_model=TruckLocationResponse)
def get_latest_truck_location(
    truck_id: int,
    db: Session = Depends(get_db)
):
    return db.query(TruckLocation).filter(
        TruckLocation.truck_id == truck_id
    ).order_by(
        TruckLocation.timestamp.desc()
    ).first()


@router.get("/truck/{truck_id}", response_model=list[TruckLocationResponse])
def get_truck_locations(
    truck_id: int,
    db: Session = Depends(get_db)
):
    return db.query(TruckLocation).filter(
        TruckLocation.truck_id == truck_id
    ).all() 