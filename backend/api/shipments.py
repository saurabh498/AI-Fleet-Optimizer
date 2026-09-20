from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.api.deps import get_current_user, require_role
from backend.models.shipment import Shipment
from backend.schemas.shipment import ShipmentCreate, ShipmentResponse


router = APIRouter(
    prefix="/shipments",
    tags=["Shipments"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/",
    response_model=ShipmentResponse,
    dependencies=[Depends(require_role("manager", "admin"))],
)
def create_shipment(
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db)
):
    shipment = Shipment(**shipment_data.model_dump())

    db.add(shipment)
    db.commit()
    db.refresh(shipment)

    return shipment


@router.get("/", response_model=list[ShipmentResponse])
def get_shipments(
    db: Session = Depends(get_db)
):
    return db.query(Shipment).all()


@router.get("/{load_id}", response_model=ShipmentResponse)
def get_shipment(
    load_id: int,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(
        Shipment.load_id == load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    return shipment


@router.put(
    "/{load_id}",
    response_model=ShipmentResponse,
    dependencies=[Depends(require_role("manager", "admin"))],
)
def update_shipment(
    load_id: int,
    shipment_data: ShipmentCreate,
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(
        Shipment.load_id == load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    for key, value in shipment_data.model_dump().items():
        setattr(shipment, key, value)

    db.commit()
    db.refresh(shipment)

    return shipment


@router.delete(
    "/{load_id}",
    dependencies=[Depends(require_role("manager", "admin"))],
)
def delete_shipment(
    load_id: int,
    db: Session = Depends(get_db)
):
    from backend.models.assignment import Assignment
    from backend.models.assignment_history import AssignmentHistory

    shipment = db.query(Shipment).filter(
        Shipment.load_id == load_id
    ).first()

    if not shipment:
        raise HTTPException(
            status_code=404,
            detail="Shipment not found"
        )

    active = db.query(Assignment).filter(
        Assignment.load_id == load_id,
        Assignment.status.in_(["assigned", "in_transit"]),
    ).first()

    if active:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot delete a shipment with an active assignment. "
                "Complete or cancel the assignment first."
            ),
        )

    shipment_assignments = db.query(Assignment).filter(
        Assignment.load_id == load_id
    ).all()

    for a in shipment_assignments:
        db.query(AssignmentHistory).filter(
            AssignmentHistory.assignment_id == a.assignment_id
        ).delete()

    db.query(Assignment).filter(
        Assignment.load_id == load_id
    ).delete()

    db.delete(shipment)
    db.commit()

    return {
        "message": "Shipment deleted successfully",
        "load_id": load_id
    }