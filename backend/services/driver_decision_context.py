'''
Combine truck, driver, and route to produce a driver feasibility
context for the decision engine.

Kept separate from driver_feasibility so the pure check stays testable
without a DB session.
'''

from sqlalchemy.orm import Session

from backend.models.driver import Driver
from backend.models.truck import Truck
from backend.services.driver_feasibility import (
    check_driver_feasibility,
    is_rules_verified,
)


DEFAULT_SPEED_KMH = 45.0


def _estimate_trip_minutes(best_match: dict | None) -> int:
    '''
    Estimate trip duration from the best_match route.
    Falls back to a conservative default if the route is missing.
    '''
    if not best_match:
        return 60

    route = best_match.get('route') or {}
    distance_km = route.get('total_distance_km')
    if not distance_km:
        distance_km = best_match.get('distance_to_pickup_km')

    if not distance_km or distance_km <= 0:
        return 60

    return max(15, int((distance_km / DEFAULT_SPEED_KMH) * 60))


def build_driver_decision_context(
    truck_id: int,
    best_match: dict | None,
    db: Session,
) -> dict | None:
    '''
    Return the driver feasibility context for this truck, or None
    if no driver is bound to the truck.
    '''
    driver = (
        db.query(Driver)
        .filter(Driver.assigned_truck_id == truck_id)
        .first()
    )
    if driver is None:
        return None

    truck = (
        db.query(Truck)
        .filter(Truck.truck_id == truck_id)
        .first()
    )
    if truck is None:
        return None

    estimated_minutes = _estimate_trip_minutes(best_match)

    result = check_driver_feasibility(driver, truck, estimated_minutes)

    return {
        'driver_id': driver.driver_id,
        'display_name': driver.display_name,
        'availability_status': driver.availability_status,
        'rest_required': driver.rest_required,
        'accumulated_driving_minutes': driver.accumulated_driving_minutes,
        'accumulated_since_last_rest_minutes': (
            driver.accumulated_since_last_rest_minutes
        ),
        'estimated_trip_minutes': estimated_minutes,
        'feasible': result['feasible'],
        'reason': result['reason'],
        'requires_review': result['requires_review'],
        'missing_data': result['missing_data'],
        'rules_verified_against_law': is_rules_verified(),
    }
