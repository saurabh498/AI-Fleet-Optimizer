from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Truck(Base):
    __tablename__ = "trucks"

    truck_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    truck_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    current_load: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    current_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    current_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    current_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="available"
    )

    destination: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    cost_per_km: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )