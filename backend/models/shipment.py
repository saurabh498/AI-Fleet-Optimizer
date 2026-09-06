from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Shipment(Base):
    __tablename__ = "shipments"

    load_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    pickup_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    pickup_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    pickup_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    destination_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    destination_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    destination_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    volume: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    cargo_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    pickup_start: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    pickup_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    delivery_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    revenue: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="available"
    )