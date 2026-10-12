from datetime import datetime, date

from sqlalchemy import String, Float, Integer, DateTime, Date, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class RestFacility(Base):
    '''
    A driver-rest facility (Apna Ghar, MoRTH Wayside Amenity, or other
    verified facility type).

    Every row MUST carry a source_url and source_date. Rows without
    them are rejected by the importer.

    verification_status tracks human review of the row:
        pending   - imported, awaiting review
        verified  - reviewed by a human and accepted
        retired   - no longer active
    '''

    __tablename__ = "rest_facilities"

    facility_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    road_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    available_amenities: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_date: Mapped[date] = mapped_column(Date, nullable=False)

    verification_status: Mapped[str] = mapped_column(
        String(20), default='pending', nullable=False
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
