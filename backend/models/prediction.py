from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    truck_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    predicted_demand: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    predicted_waiting_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    prediction_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )