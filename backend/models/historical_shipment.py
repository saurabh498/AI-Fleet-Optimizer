from datetime import date

from sqlalchemy import String, Float, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class HistoricalShipment(Base):
    __tablename__ = "historical_shipments"

    history_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    available_loads: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    completed_loads: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    average_waiting_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    average_demand: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )