from unittest.mock import MagicMock

from backend.services.backhaul_matching import find_backhaul_matches


def test_no_feasible_shipment_when_all_loads_exceed_capacity():
    truck = MagicMock()
    truck.truck_id = 1
    truck.capacity = 15000
    truck.current_load = 8000
    truck.cost_per_km = 25

    location = MagicMock()
    location.latitude = 19.076
    location.longitude = 72.8777

    oversized_shipment = MagicMock()
    oversized_shipment.load_id = 99
    oversized_shipment.pickup_city = "Mumbai"
    oversized_shipment.destination_city = "Pune"
    oversized_shipment.weight = 9000
    oversized_shipment.cargo_type = "Electronics"
    oversized_shipment.revenue = 45000
    oversized_shipment.pickup_latitude = 19.076
    oversized_shipment.pickup_longitude = 72.8777
    oversized_shipment.destination_latitude = 18.5204
    oversized_shipment.destination_longitude = 73.8567

    db = MagicMock()

    truck_query = MagicMock()
    truck_query.filter.return_value.first.return_value = truck

    location_query = MagicMock()
    location_query.filter.return_value.order_by.return_value.first.return_value = location

    shipment_query = MagicMock()
    shipment_query.filter.return_value.all.return_value = [oversized_shipment]

    db.query.side_effect = [
        truck_query,
        location_query,
        shipment_query,
    ]

    result = find_backhaul_matches(1, db)

    assert result["matches"] == []