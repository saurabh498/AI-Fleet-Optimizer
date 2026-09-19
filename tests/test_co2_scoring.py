'''
Verify CO2 emissions and total distance influence match_score.

Uses a mock DB that dispatches by model class so routing's
RouteCache lookups don't exhaust a side_effect list. OSRM
is disabled so the haversine fallback is used.
'''

from unittest.mock import MagicMock, patch

from backend.services.backhaul_matching import find_backhaul_matches


def _make_shipment(load_id, dest_lat, dest_lon, revenue, weight=8000):
    s = MagicMock()
    s.load_id = load_id
    s.pickup_city = "Mumbai"
    s.destination_city = "Delhi"
    s.pickup_latitude = 19.0760
    s.pickup_longitude = 72.8777
    s.destination_latitude = dest_lat
    s.destination_longitude = dest_lon
    s.weight = weight
    s.cargo_type = "Electronics"
    s.revenue = revenue
    return s


def _mock_db(truck, location, shipments):
    '''Mock db that dispatches query() by SQLAlchemy model class.'''

    db = MagicMock()

    def query_dispatch(model):
        q = MagicMock()
        name = getattr(model, "__name__", "")

        if name == "Truck":
            q.filter.return_value.first.return_value = truck
        elif name == "TruckLocation":
            q.filter.return_value.order_by.return_value.first.return_value = location
        elif name == "Shipment":
            q.filter.return_value.all.return_value = shipments
        elif name == "RouteCache":
            # Cache miss on read -> osrm-disabled fallback will be used
            q.filter.return_value.first.return_value = None
        else:
            q.filter.return_value.first.return_value = None
            q.filter.return_value.all.return_value = []

        return q

    db.query.side_effect = query_dispatch
    return db


def _make_truck():
    truck = MagicMock()
    truck.truck_id = 1
    truck.truck_type = "HCV"
    truck.capacity = 15000
    truck.current_load = 0
    truck.cost_per_km = 35.0
    truck.current_latitude = 19.0760
    truck.current_longitude = 72.8777
    return truck


def _make_location():
    loc = MagicMock()
    loc.latitude = 19.0760
    loc.longitude = 72.8777
    return loc


@patch("backend.services.routing.OSRM_ENABLED", False)
def test_near_load_scores_higher_than_far_load():
    '''
    Identical revenue. Near destination should score higher
    because of CO2 + total-distance penalties.
    '''

    truck = _make_truck()
    location = _make_location()

    near = _make_shipment(1, 18.5204, 73.8567, 30000)   # ~150 km
    far  = _make_shipment(2, 28.6139, 77.2090, 30000)   # ~1400 km

    db = _mock_db(truck, location, [near, far])
    result = find_backhaul_matches(1, db)
    matches = {m["load_id"]: m for m in result["matches"]}

    assert matches[1]["match_score"] > matches[2]["match_score"]


@patch("backend.services.routing.OSRM_ENABLED", False)
def test_high_co2_match_has_lower_score():
    truck = _make_truck()
    location = _make_location()

    local = _make_shipment(10, 18.5204, 73.8567, 25000)
    long_haul = _make_shipment(20, 22.5726, 88.3639, 25000)

    db = _mock_db(truck, location, [local, long_haul])
    result = find_backhaul_matches(1, db)
    matches = {m["load_id"]: m for m in result["matches"]}

    assert "co2_kg" in matches[10]
    assert matches[10]["co2_kg"] < matches[20]["co2_kg"]
    assert matches[10]["match_score"] > matches[20]["match_score"]


@patch("backend.services.routing.OSRM_ENABLED", False)
def test_reasons_include_co2():
    truck = _make_truck()
    location = _make_location()
    s = _make_shipment(1, 18.5204, 73.8567, 25000)

    db = _mock_db(truck, location, [s])
    result = find_backhaul_matches(1, db)
    reasons = " ".join(result["matches"][0]["reasons"])

    assert "CO2" in reasons
