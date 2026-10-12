from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, require_role
from backend.database.connection import get_db
from backend.models.driver import Driver
from backend.models.truck import Truck
from backend.schemas.driver import (
    DriverCreate,
    DriverFeasibilityRequest,
    DriverFeasibilityResponse,
    DriverResponse,
    DriverUpdate,
)
from backend.services.driver_feasibility import (
    check_driver_feasibility,
    is_rules_verified,
)


router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=list[DriverResponse])
def list_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).all()


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    return driver


@router.post(
    "/",
    response_model=DriverResponse,
    status_code=201,
    dependencies=[Depends(require_role("manager", "admin"))],
)
def create_driver(payload: DriverCreate, db: Session = Depends(get_db)):
    if payload.assigned_truck_id is not None:
        truck = db.query(Truck).filter(
            Truck.truck_id == payload.assigned_truck_id
        ).first()
        if not truck:
            raise HTTPException(400, "assigned_truck_id does not exist")

    driver = Driver(**payload.model_dump())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    return driver


@router.put(
    "/{driver_id}",
    response_model=DriverResponse,
    dependencies=[Depends(require_role("manager", "admin"))],
)
def update_driver(
    driver_id: int,
    payload: DriverUpdate,
    db: Session = Depends(get_db),
):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")

    data = payload.model_dump(exclude_unset=True)

    if "assigned_truck_id" in data and data["assigned_truck_id"] is not None:
        truck = db.query(Truck).filter(
            Truck.truck_id == data["assigned_truck_id"]
        ).first()
        if not truck:
            raise HTTPException(400, "assigned_truck_id does not exist")

    for key, value in data.items():
        setattr(driver, key, value)

    db.commit()
    db.refresh(driver)
    return driver


@router.delete(
    "/{driver_id}",
    dependencies=[Depends(require_role("manager", "admin"))],
)
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")

    db.delete(driver)
    db.commit()
    return {"message": "Driver deleted successfully", "driver_id": driver_id}


@router.post(
    "/{driver_id}/feasibility",
    response_model=DriverFeasibilityResponse,
)
def check_feasibility(
    driver_id: int,
    payload: DriverFeasibilityRequest,
    db: Session = Depends(get_db),
):
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")

    truck = db.query(Truck).filter(Truck.truck_id == payload.truck_id).first()
    if not truck:
        raise HTTPException(404, "Truck not found")

    result = check_driver_feasibility(
        driver, truck, payload.estimated_trip_minutes
    )
    result["rules_verified_against_law"] = is_rules_verified()
    return result
