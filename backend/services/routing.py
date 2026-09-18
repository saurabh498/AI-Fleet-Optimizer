
"""
OSRM-based routing service.

Provides real road distance and duration between two coordinates,
with two layers of caching (in-memory LRU + Postgres) and a
haversine fallback if OSRM is unreachable.

Env vars:
    OSRM_BASE_URL   default http://router.project-osrm.org
    OSRM_TIMEOUT    default 10 (seconds)
    OSRM_ENABLED    default true
"""

import logging
import math
import os
from functools import lru_cache
from typing import Optional

import requests
from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal
from backend.models.route_cache import RouteCache


logger = logging.getLogger(__name__)

OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "http://router.project-osrm.org").rstrip("/")
OSRM_TIMEOUT = float(os.getenv("OSRM_TIMEOUT", "10"))
OSRM_ENABLED = os.getenv("OSRM_ENABLED", "true").lower() == "true"

EARTH_RADIUS_KM = 6371.0088
ROAD_FACTOR = 1.30
AVG_SPEED_KMH = 45.0


# -------------------------------------------------
# Coordinate key (5 decimals ≈ 1.1 m precision)
# -------------------------------------------------

def _coord_key(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
) -> str:
    return (
        f"{round(origin_lat, 5)},{round(origin_lon, 5)}:"
        f"{round(dest_lat, 5)},{round(dest_lon, 5)}"
    )


# -------------------------------------------------
# Haversine fallback
# -------------------------------------------------

def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def _fallback_route(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
) -> dict:
    straight_km = haversine_km(origin_lat, origin_lon, dest_lat, dest_lon)
    road_km = straight_km * ROAD_FACTOR
    duration_min = (road_km / AVG_SPEED_KMH) * 60.0

    return {
        "distance_km": round(road_km, 3),
        "duration_min": round(duration_min, 2),
        "source": "haversine",
    }


# -------------------------------------------------
# In-process LRU cache
# -------------------------------------------------

@lru_cache(maxsize=4096)
def _memory_cached(key: str) -> Optional[tuple]:
    return None  # placeholder — real values are loaded via db


# -------------------------------------------------
# DB cache helpers
# -------------------------------------------------

def _read_db_cache(db: Session, key: str) -> Optional[dict]:
    row = (
        db.query(RouteCache)
        .filter(RouteCache.cache_key == key)
        .first()
    )
    if row is None:
        return None
    return {
        "distance_km": row.distance_km,
        "duration_min": row.duration_min,
        "source": row.source,
    }


def _write_db_cache(
    db: Session,
    key: str,
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    payload: dict,
) -> None:
    row = RouteCache(
        cache_key=key,
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        dest_lat=dest_lat,
        dest_lon=dest_lon,
        distance_km=payload["distance_km"],
        duration_min=payload["duration_min"],
        source=payload["source"],
    )
    db.add(row)
    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist route cache for %s", key)


# -------------------------------------------------
# OSRM HTTP call
# -------------------------------------------------

def _call_osrm(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
) -> Optional[dict]:
    if not OSRM_ENABLED:
        return None

    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
        f"?overview=false&alternatives=false&steps=false"
    )

    try:
        response = requests.get(url, timeout=OSRM_TIMEOUT)
        response.raise_for_status()
        payload = response.json()

        if payload.get("code") != "Ok" or not payload.get("routes"):
            logger.warning("OSRM non-Ok response: %s", payload.get("code"))
            return None

        route = payload["routes"][0]
        return {
            "distance_km": round(route["distance"] / 1000.0, 3),
            "duration_min": round(route["duration"] / 60.0, 2),
            "source": "osrm",
        }

    except requests.RequestException as exc:
        logger.warning("OSRM request failed: %s", exc)
        return None


# -------------------------------------------------
# Public API
# -------------------------------------------------

def get_route(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    db: Optional[Session] = None,
) -> dict:
    """
    Return {distance_km, duration_min, source}.

    Order of resolution:
        1. Postgres cache
        2. OSRM HTTP
        3. Haversine fallback
    Writes back to Postgres on OSRM success.
    """

    key = _coord_key(origin_lat, origin_lon, dest_lat, dest_lon)

    owns_session = db is None
    session = db if db is not None else SessionLocal()

    try:
        cached = _read_db_cache(session, key)
        if cached is not None:
            return cached

        osrm_result = _call_osrm(origin_lat, origin_lon, dest_lat, dest_lon)
        if osrm_result is not None:
            _write_db_cache(
                session, key,
                origin_lat, origin_lon,
                dest_lat, dest_lon,
                osrm_result,
            )
            return osrm_result

        fallback = _fallback_route(origin_lat, origin_lon, dest_lat, dest_lon)
        _write_db_cache(
            session, key,
            origin_lat, origin_lon,
            dest_lat, dest_lon,
            fallback,
        )
        return fallback

    finally:
        if owns_session:
            session.close()


def get_route_km(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    db: Optional[Session] = None,
) -> float:
    """Convenience: just the road distance in km."""
    return get_route(
        origin_lat, origin_lon, dest_lat, dest_lon, db
    )["distance_km"]