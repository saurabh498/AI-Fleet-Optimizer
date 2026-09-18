from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base


class RouteCache(Base):
    __tablename__ = "route_cache"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    cache_key: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )

    origin_lat: Mapped[float] = mapped_column(Float, nullable=False)
    origin_lon: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lat: Mapped[float] = mapped_column(Float, nullable=False)
    dest_lon: Mapped[float] = mapped_column(Float, nullable=False)

    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    duration_min: Mapped[float] = mapped_column(Float, nullable=False)

    source: Mapped[str] = mapped_column(
        String(20), nullable=False, default="osrm"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        Index("ix_route_cache_coords", "origin_lat", "origin_lon", "dest_lat", "dest_lon"),
    )
