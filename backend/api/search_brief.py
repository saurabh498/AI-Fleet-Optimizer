from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user
from backend.database.connection import get_db
from backend.schemas.search_brief import SearchBriefResponse
from backend.services.search_brief import generate_search_brief


router = APIRouter(
    prefix="/search-brief",
    tags=["External Search Brief"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/{truck_id}", response_model=SearchBriefResponse)
def create_search_brief(
    truck_id: int,
    db: Session = Depends(get_db),
):
    result = generate_search_brief(truck_id, db)
    if result is None:
        raise HTTPException(404, "Truck not found")
    return result
