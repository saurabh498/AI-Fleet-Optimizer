from unittest.mock import MagicMock

from backend.services.backhaul_matching import find_backhaul_matches


def test_no_available_shipments():
    truck = MagicMock()
    truck.truck_id = 2
    truck.capacity = 15000
    truck.current_load = 0
    truck.cost_per_km = 25

    location = MagicMock()
    location.latitude = 18.5204
    location.longitude = 73.8567

    db = MagicMock()

    truck_query = MagicMock()
    truck_query.filter.return_value.first.return_value = truck

    location_query = MagicMock()
    location_query.filter.return_value.order_by.return_value.first.return_value = location

    shipment_query = MagicMock()
    shipment_query.filter.return_value.all.return_value = []

    db.query.side_effect = [
        truck_query,
        location_query,
        shipment_query,
    ]

    result = find_backhaul_matches(2, db)

    assert result["matches"] == []