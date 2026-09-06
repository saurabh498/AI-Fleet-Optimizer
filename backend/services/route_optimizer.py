from math import radians, sin, cos, sqrt, atan2


def calculate_distance_km(
    latitude1: float,
    longitude1: float,
    latitude2: float,
    longitude2: float
) -> float:
    """
    Calculate straight-line distance between two coordinates
    using the Haversine formula.
    """

    earth_radius_km = 6371.0

    lat1 = radians(latitude1)
    lon1 = radians(longitude1)
    lat2 = radians(latitude2)
    lon2 = radians(longitude2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return round(earth_radius_km * c, 2)

def calculate_route_distances(
    truck_latitude: float,
    truck_longitude: float,
    pickup_latitude: float,
    pickup_longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    cost_per_km: float
) -> dict:
    """
    Calculate pickup distance, delivery distance,
    total trip distance and estimated transport cost.
    """

    # Distance from truck's current location to pickup
    pickup_distance = calculate_distance_km(
        truck_latitude,
        truck_longitude,
        pickup_latitude,
        pickup_longitude
    )

    # Distance from pickup location to shipment destination
    delivery_distance = calculate_distance_km(
        pickup_latitude,
        pickup_longitude,
        destination_latitude,
        destination_longitude
    )

    # Total distance
    total_distance = round(
        pickup_distance + delivery_distance,
        2
    )

    # Estimated transport cost
    estimated_cost = round(
        total_distance * cost_per_km,
        2
    )

    return {
        "pickup_distance_km": pickup_distance,
        "delivery_distance_km": delivery_distance,
        "total_distance_km": total_distance,
        "estimated_cost": estimated_cost
    }


def calculate_route_efficiency(
    revenue: float,
    total_distance_km: float,
    estimated_cost: float
) -> dict:
    """
    Calculate route profitability and efficiency score.
    """

    estimated_profit = round(
        revenue - estimated_cost,
        2
    )

    if revenue <= 0:
        efficiency_score = 0

    else:
        profit_margin = (
            estimated_profit / revenue
        ) * 100

        efficiency_score = round(
            max(0, min(100, profit_margin)),
            2
        )

    if efficiency_score >= 70:
        recommendation = "Excellent"

    elif efficiency_score >= 40:
        recommendation = "Good"

    elif efficiency_score >= 20:
        recommendation = "Moderate"

    else:
        recommendation = "Poor"

    return {
        "estimated_profit": estimated_profit,
        "efficiency_score": efficiency_score,
        "recommendation": recommendation
    }