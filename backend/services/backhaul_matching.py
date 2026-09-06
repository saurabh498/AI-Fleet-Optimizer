from math import radians, sin, cos, sqrt, atan2

from sqlalchemy.orm import Session

from backend.models.truck import Truck
from backend.models.shipment import Shipment
from backend.models.truck_location import TruckLocation

from backend.services.route_optimizer import (
    calculate_route_distances,
    calculate_route_efficiency
)

def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate approximate distance between two coordinates
    using the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius = 6371.0

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c


def calculate_waiting_time(
    available_shipment_count: int,
    unsuitable_shipment_count: int = 0,
    missing_location_count: int = 0
) -> dict:
    """
    Generate an intelligent waiting recommendation
    when no suitable backhaul shipment is available.
    """

    # Case 1: No shipments available
    if available_shipment_count == 0:
        return {
            "recommended_waiting_time_hours": 2,
            "reason": "No available backhaul shipments currently found",
            "action": "Wait and recheck for new shipments",
            "priority": "High"
        }

    # Case 2: Shipments exist but pickup location
    # information is missing
    if missing_location_count > 0:
        return {
            "recommended_waiting_time_hours": 1,
            "reason": (
                f"{missing_location_count} available shipment(s) "
                "have incomplete pickup location data"
            ),
            "action": "Wait and recheck after shipment location data is updated",
            "priority": "Medium"
        }

    # Case 3: Shipments exist but are unsuitable
    if unsuitable_shipment_count > 0:
        return {
            "recommended_waiting_time_hours": 1,
            "reason": (
                "Available backhaul shipments exist, "
                "but none are suitable for this truck"
            ),
            "action": "Recheck for a better matching shipment",
            "priority": "Medium"
        }

    # Fallback
    return {
        "recommended_waiting_time_hours": 1,
        "reason": "No suitable backhaul shipment found",
        "action": "Recheck for new shipment opportunities",
        "priority": "Medium"
    }


def find_backhaul_matches(
    truck_id: int,
    db: Session
):
    """
    Find and rank suitable backhaul shipments for a truck.

    Matching considers:
    - Latest truck location
    - Truck remaining capacity
    - Pickup distance
    - Shipment revenue
    - Capacity utilization
    - Estimated pickup cost
    - Estimated net revenue
    - Recommendation level
    - Recommendation reasons
    - Dynamic waiting time recommendation
    """

    # -------------------------------------------------
    # 1. Find truck
    # -------------------------------------------------

    truck = db.query(Truck).filter(
        Truck.truck_id == truck_id
    ).first()

    if not truck:
        return None

    # -------------------------------------------------
    # 2. Get latest truck location
    # -------------------------------------------------

    latest_location = db.query(TruckLocation).filter(
        TruckLocation.truck_id == truck_id
    ).order_by(
        TruckLocation.timestamp.desc()
    ).first()

    if not latest_location:
        return {
            "truck_id": truck_id,
            "message": "No location data available for this truck",
            "matches": []
        }

    # -------------------------------------------------
    # 3. Calculate remaining capacity
    # -------------------------------------------------

    remaining_capacity = (
        truck.capacity - truck.current_load
    )

    # -------------------------------------------------
    # 4. Get available shipments
    # -------------------------------------------------

    shipments = db.query(Shipment).filter(
        Shipment.status == "available"
    ).all()

    available_shipment_count = len(shipments)

    unsuitable_shipment_count = 0
    missing_location_count = 0

    matches = []

    # -------------------------------------------------
    # 5. Evaluate every shipment
    # -------------------------------------------------

    for shipment in shipments:

        # -------------------------------------------------
        # Skip shipments without pickup coordinates
        # -------------------------------------------------

        if (
            shipment.pickup_latitude is None
            or shipment.pickup_longitude is None
        ):
            missing_location_count += 1
            continue

        # -------------------------------------------------
        # Capacity check
        # -------------------------------------------------

        if shipment.weight > remaining_capacity:
            unsuitable_shipment_count += 1
            continue

        # -------------------------------------------------
        # Calculate distance to pickup
        # -------------------------------------------------

        distance_to_pickup = calculate_distance(
            latest_location.latitude,
            latest_location.longitude,
            shipment.pickup_latitude,
            shipment.pickup_longitude
        )

        # -------------------------------------------------
        # Calculate estimated pickup cost
        # -------------------------------------------------

        estimated_pickup_cost = (
            distance_to_pickup * truck.cost_per_km
        )

        # -------------------------------------------------
        # Calculate estimated net revenue
        # -------------------------------------------------

        estimated_net_revenue = (
            shipment.revenue - estimated_pickup_cost
        )


        # -------------------------------------------------
        # Route optimization
        # -------------------------------------------------

        if (
            shipment.destination_latitude is not None
            and shipment.destination_longitude is not None
        ):
            route = calculate_route_distances(
                truck_latitude=latest_location.latitude,
                truck_longitude=latest_location.longitude,
                pickup_latitude=shipment.pickup_latitude,
                pickup_longitude=shipment.pickup_longitude,
                destination_latitude=shipment.destination_latitude,
                destination_longitude=shipment.destination_longitude,
                cost_per_km=truck.cost_per_km
            )

            route_efficiency = calculate_route_efficiency(
                revenue=shipment.revenue,
                total_distance_km=route["total_distance_km"],
                estimated_cost=route["estimated_cost"]
            )

        else:
            route = {
                "pickup_distance_km": round(distance_to_pickup, 2),
                "delivery_distance_km": None,
                "total_distance_km": None,
                "estimated_cost": round(estimated_pickup_cost, 2)
            }

            route_efficiency = {
                "estimated_profit": round(estimated_net_revenue, 2),
                "efficiency_score": 0,
                "recommendation": "Unknown"
            }


        # -------------------------------------------------
        # Capacity utilization
        # -------------------------------------------------

        utilization = (
            shipment.weight / truck.capacity
        ) * 100

        # -------------------------------------------------
        # Start matching score
        # -------------------------------------------------

        score = 100.0

        # -------------------------------------------------
        # Distance scoring
        # -------------------------------------------------

        if distance_to_pickup <= 50:
            score += 30

        elif distance_to_pickup <= 100:
            score += 20

        elif distance_to_pickup <= 250:
            score += 10

        elif distance_to_pickup <= 500:
            score += 0

        else:
            score -= 15

        # -------------------------------------------------
        # Revenue scoring
        # -------------------------------------------------

        if shipment.revenue >= 30000:
            score += 25

        elif shipment.revenue >= 20000:
            score += 20

        elif shipment.revenue >= 10000:
            score += 15

        elif shipment.revenue >= 5000:
            score += 10

        # -------------------------------------------------
        # Capacity utilization scoring
        # -------------------------------------------------

        if utilization >= 80:
            score += 20

        elif utilization >= 60:
            score += 15

        elif utilization >= 40:
            score += 10

        elif utilization >= 20:
            score += 5

        # -------------------------------------------------
        # Net revenue scoring
        # -------------------------------------------------

        if estimated_net_revenue >= 25000:
            score += 20

        elif estimated_net_revenue >= 15000:
            score += 15

        elif estimated_net_revenue >= 10000:
            score += 10

        elif estimated_net_revenue >= 5000:
            score += 5

        elif estimated_net_revenue < 0:
            score -= 20

        # -------------------------------------------------
        # Cost efficiency scoring
        # -------------------------------------------------

        if distance_to_pickup > 0:

            revenue_per_km = (
                shipment.revenue / distance_to_pickup
            )

            if revenue_per_km >= 100:
                score += 10

            elif revenue_per_km >= 50:
                score += 5


        # -------------------------------------------------
        # Route efficiency scoring
        # -------------------------------------------------

        efficiency_score = route_efficiency["efficiency_score"]

        if efficiency_score >= 70:
          score += 20

        elif efficiency_score >= 40:
          score += 10

        elif efficiency_score >= 20:
          score += 5

        else:
         score -= 10       

        # -------------------------------------------------
        # Generate recommendation reasons
        # -------------------------------------------------

        reasons = []

        # -------------------------------------------------
        # Distance reason
        # -------------------------------------------------

        if distance_to_pickup <= 50:

            reasons.append(
                "Pickup is within 50 km"
            )

        elif distance_to_pickup <= 100:

            reasons.append(
                "Pickup is within 100 km"
            )

        elif distance_to_pickup <= 250:

            reasons.append(
                "Pickup is within 250 km"
            )

        elif distance_to_pickup <= 500:

            reasons.append(
                "Pickup is within 500 km"
            )

        else:

            reasons.append(
                "Pickup is far from current truck location"
            )

        # -------------------------------------------------
        # Revenue reason
        # -------------------------------------------------

        if shipment.revenue >= 30000:

            reasons.append(
                f"High shipment revenue of ₹{shipment.revenue:,.2f}"
            )

        elif shipment.revenue >= 10000:

            reasons.append(
                f"Good shipment revenue of ₹{shipment.revenue:,.2f}"
            )

        else:

            reasons.append(
                f"Shipment revenue is ₹{shipment.revenue:,.2f}"
            )

        # -------------------------------------------------
        # Capacity reason
        # -------------------------------------------------

        if utilization >= 80:

            reasons.append(
                f"High capacity utilization of {utilization:.2f}%"
            )

        elif utilization >= 60:

            reasons.append(
                f"Good capacity utilization of {utilization:.2f}%"
            )

        elif utilization >= 40:

            reasons.append(
                f"Moderate capacity utilization of {utilization:.2f}%"
            )

        else:

            reasons.append(
                f"Low capacity utilization of {utilization:.2f}%"
            )

        # -------------------------------------------------
        # Net revenue reason
        # -------------------------------------------------

        if estimated_net_revenue >= 25000:

            reasons.append(
                "Excellent estimated net revenue of "
                f"₹{estimated_net_revenue:,.2f}"
            )

        elif estimated_net_revenue >= 15000:

            reasons.append(
                "Good estimated net revenue of "
                f"₹{estimated_net_revenue:,.2f}"
            )

        elif estimated_net_revenue >= 5000:

            reasons.append(
                "Positive estimated net revenue of "
                f"₹{estimated_net_revenue:,.2f}"
            )

        else:

            reasons.append(
                "Low estimated net revenue of "
                f"₹{estimated_net_revenue:,.2f}"
            )

        # -------------------------------------------------
        # Cost reason
        # -------------------------------------------------

        if (
            distance_to_pickup <= 100
            and estimated_pickup_cost < shipment.revenue * 0.10
        ):

            reasons.append(
                "Low pickup cost compared with shipment revenue"
            )

        elif estimated_pickup_cost < shipment.revenue * 0.25:

            reasons.append(
                "Pickup cost is reasonable compared with revenue"
            )

        else:

            reasons.append(
                "Pickup cost is relatively high"
            )


        # -------------------------------------------------
        # Route efficiency reason
        # -------------------------------------------------

        if efficiency_score >= 70:

            reasons.append(
                f"Excellent route efficiency of "
                f"{efficiency_score:.2f}%"
            )

        elif efficiency_score >= 40:

            reasons.append(
                f"Good route efficiency of "
                f"{efficiency_score:.2f}%"
            )

        elif efficiency_score >= 20:

            reasons.append(
                f"Moderate route efficiency of "
                f"{efficiency_score:.2f}%"
            )

        else:

            reasons.append(
                f"Low route efficiency of "
                f"{efficiency_score:.2f}%"
            )
        
        # -------------------------------------------------
        # Recommendation level
        # -------------------------------------------------

        if score >= 180:

            recommendation = "Highly Recommended"

        elif score >= 150:

            recommendation = "Recommended"

        elif score >= 120:

            recommendation = "Moderately Recommended"

        else:

            recommendation = "Low Priority"

        # -------------------------------------------------
        # Store match
        # -------------------------------------------------

        matches.append({

            "load_id": shipment.load_id,

            "pickup_city": shipment.pickup_city,

            "destination_city": shipment.destination_city,

            "weight": shipment.weight,

            "cargo_type": shipment.cargo_type,

            "revenue": shipment.revenue,

            "distance_to_pickup_km": round(
                distance_to_pickup,
                2
            ),

            "estimated_pickup_cost": round(
                estimated_pickup_cost,
                2
            ),

            "estimated_net_revenue": round(
                estimated_net_revenue,
                2
            ),

            "route": route,

            "estimated_route_cost": route["estimated_cost"],

            "estimated_route_profit": route_efficiency[
                 "estimated_profit"
            ],

            "route_efficiency_score": route_efficiency[
                 "efficiency_score"
            ],

            "route_recommendation": route_efficiency[
                 "recommendation"
            ],

            "capacity_utilization_percent": round(
                utilization,
                2
            ),

            "match_score": round(
                score,
                2
            ),

            "recommendation": recommendation,

            "reasons": reasons
        })

    # -------------------------------------------------
    # 6. Sort by best match
    # -------------------------------------------------

    matches.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    # -------------------------------------------------
    # 7. No matches
    # -------------------------------------------------

    if not matches:

        waiting_recommendation = calculate_waiting_time(
            available_shipment_count,
            unsuitable_shipment_count,
            missing_location_count
        )

        return {
            "truck_id": truck_id,

            "current_location": {
                "latitude": latest_location.latitude,
                "longitude": latest_location.longitude
            },

            "remaining_capacity": remaining_capacity,

            "message": "No suitable backhaul shipment found",

            "waiting_recommendation": waiting_recommendation,

            "matches": []
        }

    # -------------------------------------------------
    # 8. Return recommendations
    # -------------------------------------------------

    return {
        "truck_id": truck_id,

        "current_location": {
            "latitude": latest_location.latitude,
            "longitude": latest_location.longitude
        },

        "remaining_capacity": remaining_capacity,

        "message": "Backhaul matches found",

        "matches": matches
    }