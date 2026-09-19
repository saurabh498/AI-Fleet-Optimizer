from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.api.deps import get_current_user, require_role
from backend.models.truck_location import TruckLocation
from backend.models.truck import Truck
from backend.schemas.truck_location import (
    TruckLocationCreate,
    TruckLocationResponse
)


router = APIRouter(
    prefix="/locations",
    tags=["Truck Locations"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    response_model=TruckLocationResponse,
    dependencies=[Depends(require_role("driver", "manager", "admin"))],
)
def create_location(
    location_data: TruckLocationCreate,
    db: Session = Depends(get_db)
):
    import math

    # -------------------------------------------------
    # 1. Validate latitude
    # -------------------------------------------------

    if not math.isfinite(location_data.latitude):
        raise HTTPException(
            status_code=400,
            detail="Latitude must be a finite number"
        )

    if not -90 <= location_data.latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90"
        )

    # -------------------------------------------------
    # 2. Validate longitude
    # -------------------------------------------------

    if not math.isfinite(location_data.longitude):
        raise HTTPException(
            status_code=400,
            detail="Longitude must be a finite number"
        )

    if not -180 <= location_data.longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180"
        )

    # -------------------------------------------------
    # 3. Validate truck
    # -------------------------------------------------

    truck = db.query(Truck).filter(
        Truck.truck_id == location_data.truck_id
    ).first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail="Truck not found"
        )

    # -------------------------------------------------
    # 4. Create GPS location
    # -------------------------------------------------

    location = TruckLocation(
        **location_data.model_dump()
    )

    db.add(location)

    # Synchronize latest GPS position with Truck table
    truck.current_latitude = location_data.latitude
    truck.current_longitude = location_data.longitude

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