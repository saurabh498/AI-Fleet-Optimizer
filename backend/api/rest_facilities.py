from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, require_role
from backend.database.connection import get_db
from backend.models.rest_facility import RestFacility
from backend.schemas.rest_facility import (
    RestFacilityCreate,
    RestFacilityImportRequest,
    RestFacilityImportResult,
    RestFacilityResponse,
)
from backend.services.rest_facility_import import import_csv


router = APIRouter(
    prefix='/rest-facilities',
    tags=['Rest Facilities'],
    dependencies=[Depends(get_current_user)],
)


@router.get('/', response_model=list[RestFacilityResponse])
def list_facilities(db: Session = Depends(get_db)):
    return db.query(RestFacility).order_by(RestFacility.name).all()


@router.get('/{facility_id}', response_model=RestFacilityResponse)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = db.query(RestFacility).filter(
        RestFacility.facility_id == facility_id
    ).first()
    if not facility:
        raise HTTPException(404, 'Facility not found')
    return facility


@router.post(
    '/',
    response_model=RestFacilityResponse,
    status_code=201,
    dependencies=[Depends(require_role('manager', 'admin'))],
)
def create_facility(
    payload: RestFacilityCreate,
    db: Session = Depends(get_db),
):
    existing = db.query(RestFacility).filter(
        RestFacility.name == payload.name,
        RestFacility.latitude == payload.latitude,
        RestFacility.longitude == payload.longitude,
    ).first()
    if existing:
        raise HTTPException(409, 'Facility already exists at these coordinates')

    facility = RestFacility(**payload.model_dump())
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility


@router.post(
    '/import-csv',
    response_model=RestFacilityImportResult,
    dependencies=[Depends(require_role('manager', 'admin'))],
)
def import_facilities_csv(
    payload: RestFacilityImportRequest,
    db: Session = Depends(get_db),
):
    return import_csv(payload.filename, db)


@router.delete(
    '/{facility_id}',
    dependencies=[Depends(require_role('manager', 'admin'))],
)
def delete_facility(facility_id: int, db: Session = Depends(get_db)):
    facility = db.query(RestFacility).filter(
        RestFacility.facility_id == facility_id
    ).first()
    if not facility:
        raise HTTPException(404, 'Facility not found')
    db.delete(facility)
    db.commit()
    return {'message': 'Facility deleted', 'facility_id': facility_id}
