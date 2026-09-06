from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Assignment(Base):
    __tablename__ = "assignments"

    assignment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    truck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("trucks.truck_id"),
        nullable=False
    )

    load_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("shipments.load_id"),
        nullable=False
    )

    match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    estimated_distance: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    estimated_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    estimated_profit: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    waiting_time: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    recommendation: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="assigned",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )