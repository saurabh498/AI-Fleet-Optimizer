'''RestFacility suggestion on WAIT / REPOSITION decisions.'''

from datetime import date

from backend.database.connection import SessionLocal
from backend.models.driver import Driver
from backend.models.rest_facility import RestFacility
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation
from backend.services.driver_feasibility import get_rule
from backend.services.rest_facility_recommendation import (
    suggest_rest_facility,
)


# -------------------------------------------------
# Fixture helpers - all return IDs, all cleanup by ID
# -------------------------------------------------

def _make_truck(db, **overrides):
    defaults = dict(
        truck_type='HCV',
        capacity=15000,
        current_load=0,
        cost_per_km=35.0,
        status='available',
        current_city='Mumbai',
        current_latitude=19.0760,
        current_longitude=72.8777,
    )
    defaults.update(overrides)
    t = Truck(**defaults)
    db.add(t)
    db.flush()
    return t.truck_id


def _make_driver(db, truck_id, **overrides):
    defaults = dict(
        display_name='Rest Test Driver',
        availability_status='available',
        assigned_truck_id=truck_id,
        accumulated_driving_minutes=0,
        accumulated_since_last_rest_minutes=0,
        rest_required=False,
    )
    defaults.update(overrides)
    d = Driver(**defaults)
    db.add(d)
    db.flush()
    return d.driver_id


def _make_facility(db, **overrides):
    defaults = dict(
        name='Test Verified Facility',
        facility_type='apna_ghar',
        latitude=19.10,
        longitude=72.90,
        source_url='https://example.invalid/test',
        source_date=date(2026, 1, 15),
        verification_status='verified',
    )
    defaults.update(overrides)
    f = RestFacility(**defaults)
    db.add(f)
    db.flush()
    return f.facility_id


def _teardown(truck_id=None, driver_id=None, facility_id=None):
    '''FK-safe cleanup of specific rows only.'''
    db = SessionLocal()
    try:
        db.rollback()
    except Exception:
        pass
    try:
        if truck_id is not None:
            db.query(TruckLocation).filter(
                TruckLocation.truck_id == truck_id
            ).delete()
        if facility_id is not None:
            db.query(RestFacility).filter(
                RestFacility.facility_id == facility_id
            ).delete()
        if driver_id is not None:
            db.query(Driver).filter(
                Driver.driver_id == driver_id
            ).delete()
        if truck_id is not None:
            db.query(Truck).filter(
                Truck.truck_id == truck_id
            ).delete()
        db.commit()
    finally:
        db.close()


def _run(fn):
    '''Helper: run a test body inside a session, ensuring teardown.'''
    db = SessionLocal()
    ids = {'truck': None, 'driver': None, 'facility': None}
    try:
        result = fn(db, ids)
    finally:
        db.close()
        _teardown(
            truck_id=ids['truck'],
            driver_id=ids['driver'],
            facility_id=ids['facility'],
        )
    return result


# -------------------------------------------------
# Trigger conditions
# -------------------------------------------------

def test_no_suggestion_when_decision_is_assign_now():
    def body(db, ids):
        ids['truck'] = _make_truck(db)
        ids['driver'] = _make_driver(
            db, ids['truck'], rest_required=True
        )
        ids['facility'] = _make_facility(db)
        db.commit()
        return suggest_rest_facility(
            ids['truck'], 'ASSIGN_NOW', db
        )

    assert _run(body) is None


def test_no_suggestion_when_driver_within_limits():
    def body(db, ids):
        ids['truck'] = _make_truck(db)
        ids['driver'] = _make_driver(db, ids['truck'])
        ids['facility'] = _make_facility(db)
        db.commit()
        return suggest_rest_facility(ids['truck'], 'WAIT', db)

    assert _run(body) is None


# -------------------------------------------------
# WAIT + rest required + verified facility
# -------------------------------------------------

def test_wait_gets_suggestion_when_rest_required():
    def body(db, ids):
        ids['truck'] = _make_truck(db)
        ids['driver'] = _make_driver(
            db, ids['truck'], rest_required=True
        )
        ids['facility'] = _make_facility(db)
        db.commit()
        return suggest_rest_facility(ids['truck'], 'WAIT', db)

    r = _run(body)
    assert r is not None
    assert r['recommended_action_label'] == 'WAIT_AT_REST_FACILITY'
    assert r['facility'] is not None
    assert r['facility']['name'] == 'Test Verified Facility'
    assert r['facility']['verification_status'] == 'verified'
    assert r['facility']['distance_km'] is not None
    assert r['requires_review'] is True


# -------------------------------------------------
# REPOSITION uses the other label
# -------------------------------------------------

def test_reposition_uses_reposition_label():
    def body(db, ids):
        ids['truck'] = _make_truck(db)
        ids['driver'] = _make_driver(
            db, ids['truck'], rest_required=True
        )
        ids['facility'] = _make_facility(db)
        db.commit()
        return suggest_rest_facility(ids['truck'], 'REPOSITION', db)

    r = _run(body)
    assert r is not None
    assert r['recommended_action_label'] == 'REPOSITION_TO_REST_FACILITY'


# -------------------------------------------------
# Trigger by approaching threshold (not rest_required)
# -------------------------------------------------

def test_approaching_threshold_triggers_suggestion():
    def body(db, ids):
        max_cont = get_rule('max_continuous_driving_minutes')
        near = int(max_cont * 0.8)
        ids['truck'] = _make_truck(db)
        ids['driver'] = _make_driver(
            db, ids['truck'],
            rest_required=False,
            accumulated_since_last_rest_minutes=near,
        )
        ids['facility'] = _make_facility(db)
        db.commit()
        return suggest_rest_facility(ids['truck'], 'WAIT', db)

    r = _run(body)
    assert r is not None
    assert r['facility'] is not None


# -------------------------------------------------
# Only verified facilities used
# -------------------------------------------------

def test_pending_facility_is_ignored():
    def body(db, ids):
        ids['truck'] = _make_truck(db)
        ids['driver'] = _make_driver(
            db, ids['truck'], rest_required=True
        )
        ids['facility'] = _make_facility(
            db, verification_status='pending'
        )
        db.commit()
        return suggest_rest_facility(ids['truck'], 'WAIT', db)

    r = _run(body)
    assert r is not None
    assert r['facility'] is None
    assert 'no verified rest facility' in r['reason']


# -------------------------------------------------
# Truck with no coordinates
# -------------------------------------------------

def test_missing_truck_coords_requires_review():
    def body(db, ids):
        ids['truck'] = _make_truck(
            db, current_latitude=None, current_longitude=None
        )
        ids['driver'] = _make_driver(
            db, ids['truck'], rest_required=True
        )
        ids['facility'] = _make_facility(db)
        db.commit()
        return suggest_rest_facility(ids['truck'], 'WAIT', db)

    r = _run(body)
    assert r is not None
    assert r['facility'] is None
    assert 'no coordinates' in r['reason'].lower()
    assert r['requires_review'] is True


# -------------------------------------------------
# No driver at all
# -------------------------------------------------

def test_no_driver_returns_none():
    def body(db, ids):
        ids['truck'] = _make_truck(db)
        db.commit()
        return suggest_rest_facility(ids['truck'], 'WAIT', db)

    assert _run(body) is None
