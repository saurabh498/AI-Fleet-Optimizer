'''
Suggest a verified rest facility for a driver who needs rest,
to be attached as an annotation on WAIT / REPOSITION decisions.

CRITICAL RULES:
- Only verification_status == 'verified' facilities are used.
- Distances come from the existing routing service (OSRM + cache).
  If OSRM is down, the haversine fallback is used and the response
  marks source='haversine' explicitly.
- If no verified facility is found, we still return a suggestion
  object explaining that - we never silently drop the annotation.
'''

from sqlalchemy.orm import Session

from backend.models.driver import Driver
from backend.models.rest_facility import RestFacility
from backend.models.truck import Truck
from backend.services.driver_feasibility import get_rule
from backend.services.routing import get_route


# Bounding box in degrees (~222 km per degree of latitude)
LAT_SPAN = 2.0
LON_SPAN = 2.0

# Max candidates to route-check (avoids blowing up on big databases)
MAX_CANDIDATES = 20

# How many facilities to return
TOP_N = 3

# Approaching-limit threshold: fraction of max continuous driving
APPROACHING_RATIO = 0.75


def _driver_needs_rest(driver: Driver) -> tuple[bool, str]:
    '''Return (needs_rest, reason).'''
    if driver is None:
        return False, 'no driver bound'

    if driver.rest_required:
        return True, 'driver.rest_required is True'

    max_cont = get_rule('max_continuous_driving_minutes')
    if max_cont and driver.accumulated_since_last_rest_minutes is not None:
        threshold = int(max_cont * APPROACHING_RATIO)
        if driver.accumulated_since_last_rest_minutes >= threshold:
            return True, (
                f'accumulated_since_last_rest_minutes '
                f'({driver.accumulated_since_last_rest_minutes}) '
                f'>= {int(APPROACHING_RATIO * 100)}% of limit ({max_cont})'
            )

    return False, 'driver is within limits'


def _bbox_query(truck: Truck, db: Session) -> list:
    '''Return up to MAX_CANDIDATES verified facilities near the truck.'''
    lat = truck.current_latitude
    lon = truck.current_longitude

    return (
        db.query(RestFacility)
        .filter(RestFacility.verification_status == 'verified')
        .filter(RestFacility.latitude >= lat - LAT_SPAN)
        .filter(RestFacility.latitude <= lat + LAT_SPAN)
        .filter(RestFacility.longitude >= lon - LON_SPAN)
        .filter(RestFacility.longitude <= lon + LON_SPAN)
        .limit(MAX_CANDIDATES)
        .all()
    )


def _action_label(decision: str) -> str:
    if decision == 'REPOSITION':
        return 'REPOSITION_TO_REST_FACILITY'
    return 'WAIT_AT_REST_FACILITY'


def suggest_rest_facility(
    truck_id: int,
    decision: str,
    db: Session,
) -> dict | None:
    '''
    Return a suggestion dict, or None if:
      - decision is not WAIT or REPOSITION
      - no driver is bound to the truck
      - driver does not need rest
      - truck has no coordinates

    Always returns a dict (with facility=None and requires_review=True)
    if the driver needs rest but no verified facility is available.
    '''
    if decision not in ('WAIT', 'REPOSITION'):
        return None

    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if truck is None:
        return None

    driver = (
        db.query(Driver)
        .filter(Driver.assigned_truck_id == truck_id)
        .first()
    )
    if driver is None:
        return None

    needs_rest, rest_reason = _driver_needs_rest(driver)
    if not needs_rest:
        return None

    if truck.current_latitude is None or truck.current_longitude is None:
        return {
            'recommended_action_label': _action_label(decision),
            'facility': None,
            'alternatives': [],
            'requires_review': True,
            'reason': (
                'Driver needs rest but truck has no coordinates; '
                'cannot search for a facility'
            ),
            'rest_trigger': rest_reason,
        }

    candidates = _bbox_query(truck, db)

    if not candidates:
        return {
            'recommended_action_label': _action_label(decision),
            'facility': None,
            'alternatives': [],
            'requires_review': True,
            'reason': (
                'Driver needs rest but no verified rest facility was '
                'found near the truck'
            ),
            'rest_trigger': rest_reason,
        }

    routed: list[dict] = []
    for facility in candidates:
        try:
            route = get_route(
                truck.current_latitude,
                truck.current_longitude,
                facility.latitude,
                facility.longitude,
                db=db,
            )
        except Exception as exc:
            routed.append({
                'facility_id': facility.facility_id,
                'name': facility.name,
                'facility_type': facility.facility_type,
                'latitude': facility.latitude,
                'longitude': facility.longitude,
                'distance_km': None,
                'duration_min': None,
                'distance_source': 'error',
                'error': str(exc),
            })
            continue

        routed.append({
            'facility_id': facility.facility_id,
            'name': facility.name,
            'facility_type': facility.facility_type,
            'latitude': facility.latitude,
            'longitude': facility.longitude,
            'road_reference': facility.road_reference,
            'available_amenities': facility.available_amenities,
            'source_url': facility.source_url,
            'source_date': facility.source_date.isoformat(),
            'verification_status': facility.verification_status,
            'distance_km': route['distance_km'],
            'duration_min': route['duration_min'],
            'distance_source': route['source'],
        })

    usable = [r for r in routed if r.get('distance_km') is not None]
    errored = [r for r in routed if r.get('distance_km') is None]

    usable.sort(key=lambda r: r['distance_km'])
    top = usable[:TOP_N]
    alternatives = usable[TOP_N:]

    any_haversine = any(r['distance_source'] == 'haversine' for r in top)
    all_errored = len(usable) == 0

    if all_errored:
        reason = (
            'Driver needs rest but route lookup failed for every '
            'nearby facility; manual review required'
        )
    elif any_haversine:
        reason = (
            'Driver needs rest. Nearest verified facility suggested '
            'with straight-line (haversine) distance because the '
            'road-routing service was unavailable.'
        )
    else:
        reason = 'Driver needs rest. Nearest verified facility suggested.'

    return {
        'recommended_action_label': _action_label(decision),
        'facility': top[0] if top else None,
        'alternatives': alternatives,
        'requires_review': True,
        'reason': reason,
        'rest_trigger': rest_reason,
        'errored_facilities': errored if errored else None,
    }
