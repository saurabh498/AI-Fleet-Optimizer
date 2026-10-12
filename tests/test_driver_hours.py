'''Driver hours accumulation tests.'''

from datetime import datetime, timedelta

from backend.database.connection import SessionLocal
from backend.models.assignment import Assignment
from backend.models.assignment_history import AssignmentHistory
from backend.models.driver import Driver
from backend.models.shipment import Shipment
from backend.models.truck import Truck
from backend.services.driver_hours import (
    apply_completion_to_driver,
    apply_rest_taken,
    get_driver_for_truck,
)
from backend.services.driver_feasibility import get_rule


def _make_truck(db):
    t = Truck(
        truck_type='HCV',
        capacity=15000,
        current_load=0,
        cost_per_km=35.0,
        status='available',
        current_city='Mumbai',
    )
    db.add(t)
    db.flush()
    return t


def _make_shipment(db, tag):
    s = Shipment(
        pickup_city='Mumbai',
        pickup_latitude=19.0760,
        pickup_longitude=72.8777,
        destination_city='Pune',
        destination_latitude=18.5204,
        destination_longitude=73.8567,
        weight=5000,
        cargo_type='Test',
        revenue=20000,
        status='available',
    )
    db.add(s)
    db.flush()
    return s


def _cleanup(db, truck_id, driver_id, shipment_id=None, assignment_id=None):
    try:
        db.rollback()
    except Exception:
        pass

    if assignment_id:
        db.query(AssignmentHistory).filter(
            AssignmentHistory.assignment_id == assignment_id
        ).delete()
        db.query(Assignment).filter(
            Assignment.assignment_id == assignment_id
        ).delete()
    if driver_id:
        db.query(Driver).filter(Driver.driver_id == driver_id).delete()
    if truck_id:
        db.query(Truck).filter(Truck.truck_id == truck_id).delete()
    if shipment_id:
        db.query(Shipment).filter(Shipment.load_id == shipment_id).delete()
    db.commit()


# -------------------------------------------------
# get_driver_for_truck
# -------------------------------------------------

def test_get_driver_for_truck_returns_none_when_unbound():
    db = SessionLocal()
    try:
        assert get_driver_for_truck(999999, db) is None
    finally:
        db.close()


def test_get_driver_for_truck_returns_bound_driver():
    db = SessionLocal()
    t = _make_truck(db)
    d = Driver(
        display_name='Test Bound Driver',
        availability_status='available',
        assigned_truck_id=t.truck_id,
    )
    db.add(d)
    db.commit()
    try:
        found = get_driver_for_truck(t.truck_id, db)
        assert found is not None
        assert found.driver_id == d.driver_id
    finally:
        _cleanup(db, t.truck_id, d.driver_id)
        db.close()


# -------------------------------------------------
# apply_completion_to_driver
# -------------------------------------------------

def test_completion_without_driver_is_noop():
    db = SessionLocal()
    t = _make_truck(db)
    s = _make_shipment(db, 'noop')
    a = Assignment(
        truck_id=t.truck_id,
        load_id=s.load_id,
        match_score=100,
        estimated_distance=100,
        estimated_cost=1000,
        estimated_profit=100,
        waiting_time=0,
        recommendation='Recommended',
        status='completed',
    )
    db.add(a)
    db.commit()
    try:
        r = apply_completion_to_driver(a, db)
        assert r is None
    finally:
        _cleanup(db, t.truck_id, None, s.load_id, a.assignment_id)
        db.close()


def test_completion_accumulates_minutes():
    db = SessionLocal()
    t = _make_truck(db)
    s = _make_shipment(db, 'acc')
    d = Driver(
        display_name='Test Accumulate',
        availability_status='available',
        assigned_truck_id=t.truck_id,
        accumulated_driving_minutes=0,
        accumulated_since_last_rest_minutes=0,
    )
    db.add(d)
    db.flush()

    a = Assignment(
        truck_id=t.truck_id,
        load_id=s.load_id,
        match_score=100,
        estimated_distance=100,
        estimated_cost=1000,
        estimated_profit=100,
        waiting_time=0,
        recommendation='Recommended',
        status='completed',
    )
    db.add(a)
    db.flush()

    h = AssignmentHistory(
        assignment_id=a.assignment_id,
        status='in_transit',
        changed_at=datetime.utcnow() - timedelta(minutes=30),
    )
    db.add(h)
    db.commit()

    try:
        r = apply_completion_to_driver(a, db)
        assert r is not None
        assert 28 <= r['elapsed_minutes'] <= 32
        assert r['accumulated_driving_minutes'] >= 28
    finally:
        _cleanup(db, t.truck_id, d.driver_id, s.load_id, a.assignment_id)
        db.close()


def test_completion_triggers_rest_when_continuous_limit_reached():
    db = SessionLocal()
    t = _make_truck(db)
    s = _make_shipment(db, 'rest')
    d = Driver(
        display_name='Test Rest Trigger',
        availability_status='available',
        assigned_truck_id=t.truck_id,
        accumulated_driving_minutes=0,
        accumulated_since_last_rest_minutes=0,
    )
    db.add(d)
    db.flush()

    a = Assignment(
        truck_id=t.truck_id,
        load_id=s.load_id,
        match_score=100,
        estimated_distance=100,
        estimated_cost=1000,
        estimated_profit=100,
        waiting_time=0,
        recommendation='Recommended',
        status='completed',
    )
    db.add(a)
    db.flush()

    max_c = get_rule('max_continuous_driving_minutes')
    over = max_c + 5
    h = AssignmentHistory(
        assignment_id=a.assignment_id,
        status='in_transit',
        changed_at=datetime.utcnow() - timedelta(minutes=over),
    )
    db.add(h)
    db.commit()

    try:
        r = apply_completion_to_driver(a, db)
        assert r['rest_required'] is True
        assert 'max_continuous_driving_minutes' in r['thresholds_triggered']
        assert r['rules_verified_against_law'] is False
    finally:
        _cleanup(db, t.truck_id, d.driver_id, s.load_id, a.assignment_id)
        db.close()


def test_completion_without_history_does_not_crash():
    db = SessionLocal()
    t = _make_truck(db)
    s = _make_shipment(db, 'hist')
    d = Driver(
        display_name='Test No History',
        availability_status='available',
        assigned_truck_id=t.truck_id,
    )
    db.add(d)
    db.flush()

    a = Assignment(
        truck_id=t.truck_id,
        load_id=s.load_id,
        match_score=100,
        estimated_distance=100,
        estimated_cost=1000,
        estimated_profit=100,
        waiting_time=0,
        recommendation='Recommended',
        status='completed',
    )
    db.add(a)
    db.commit()

    try:
        r = apply_completion_to_driver(a, db)
        assert r is not None
        assert r['elapsed_minutes'] == 0
    finally:
        _cleanup(db, t.truck_id, d.driver_id, s.load_id, a.assignment_id)
        db.close()


# -------------------------------------------------
# apply_rest_taken
# -------------------------------------------------

def test_rest_taken_resets_counters():
    db = SessionLocal()
    d = Driver(
        display_name='Test Rest Reset',
        availability_status='available',
        accumulated_driving_minutes=500,
        accumulated_since_last_rest_minutes=300,
        rest_required=True,
    )
    db.add(d)
    db.commit()
    try:
        r = apply_rest_taken(d, db)
        assert r['rest_required'] is False
        assert r['accumulated_since_last_rest_minutes'] == 0
        db.refresh(d)
        assert d.accumulated_driving_minutes == 500
    finally:
        db.query(Driver).filter(Driver.driver_id == d.driver_id).delete()
        db.commit()
        db.close()
