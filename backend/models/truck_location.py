from datetime import datetime

from sqlalchemy import Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class TruckLocation(Base):
    __tablename__ = "truck_locations"

    location_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    truck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trucks.truck_id"),
        nullable=False
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    speed: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )