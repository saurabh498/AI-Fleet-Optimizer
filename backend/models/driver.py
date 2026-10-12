from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class Driver(Base):
    '''
    A fleet driver.

    May be linked to a User account (role='driver') for auth,
    and optionally to the currently assigned Truck.

    Location: when assigned_truck_id is set, the truck's location
    is the source of truth. current_latitude/longitude are a
    fallback for unassigned drivers.

    NOTE: accumulated_* fields are placeholders. Driving-hour and
    rest rules are configurable and NOT legally verified - see
    config/driver_rules.yaml.
    '''

    __tablename__ = "drivers"

    driver_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True,
        unique=True,
    )

    assigned_truck_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("trucks.truck_id"),
        nullable=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(120), nullable=False
    )

    availability_status: Mapped[str] = mapped_column(
        String(30), default="available", nullable=False
    )

    current_latitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    current_longitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    shift_start: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    shift_end: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    accumulated_driving_minutes: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    accumulated_since_last_rest_minutes: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    last_rest_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    rest_required: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
