
from unittest.mock import MagicMock, patch

from backend.services import routing


# -------------------------------------------------
# Haversine sanity
# -------------------------------------------------

def test_haversine_mumbai_to_pune():
    km = routing.haversine_km(19.0760, 72.8777, 18.5204, 73.8567)
    assert 100 < km < 160


# -------------------------------------------------
# Fallback when OSRM disabled
# -------------------------------------------------

def test_fallback_when_osrm_disabled():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with patch.object(routing, "OSRM_ENABLED", False):
        result = routing.get_route(
            19.0760, 72.8777, 18.5204, 73.8567, db=db
        )

    assert result["source"] == "haversine"
    assert result["distance_km"] > 0
    assert result["duration_min"] > 0
    db.add.assert_called_once()


# -------------------------------------------------
# Cache hit short-circuits OSRM
# -------------------------------------------------

def test_cache_hit_short_circuits():
    db = MagicMock()
    cache_row = MagicMock()
    cache_row.distance_km = 150.0
    cache_row.duration_min = 180.0
    cache_row.source = "osrm"
    db.query.return_value.filter.return_value.first.return_value = cache_row

    with patch.object(routing, "_call_osrm") as mock_osrm:
        result = routing.get_route(
            19.0760, 72.8777, 18.5204, 73.8567, db=db
        )

    mock_osrm.assert_not_called()
    assert result["distance_km"] == 150.0
    assert result["source"] == "osrm"


# -------------------------------------------------
# OSRM success path writes to cache
# -------------------------------------------------

def test_osrm_success_writes_cache():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    fake_osrm = {
        "distance_km": 149.5,
        "duration_min": 185.0,
        "source": "osrm",
    }

    with patch.object(routing, "_call_osrm", return_value=fake_osrm):
        result = routing.get_route(
            19.0760, 72.8777, 18.5204, 73.8567, db=db
        )

    assert result["source"] == "osrm"
    assert result["distance_km"] == 149.5
    db.add.assert_called_once()


# -------------------------------------------------
# Convenience helper
# -------------------------------------------------

def test_get_route_km():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with patch.object(routing, "OSRM_ENABLED", False):
        km = routing.get_route_km(
            19.0760, 72.8777, 18.5204, 73.8567, db=db
        )

    assert km > 0
