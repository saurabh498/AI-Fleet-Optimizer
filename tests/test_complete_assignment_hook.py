'''Verify that complete_assignment triggers driver hours tracking.'''

from datetime import datetime, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.database.connection import SessionLocal
from backend.main import app
from backend.models.assignment import Assignment
from backend.models.assignment_history import AssignmentHistory
from backend.models.driver import Driver
from backend.models.shipment import Shipment
from backend.models.truck import Truck


client = TestClient(app)


def _login(email, password):
    r = client.post(
        '/auth/login', json={'email': email, 'password': password}
    )
    assert r.status_code == 200, r.text
    return r.json()['access_token']


def _hdr(token):
    return {'Authorization': f'Bearer {token}'}


def _setup_assignment_in_transit():
    '''Create truck + driver + shipment + assignment in in_transit state.'''
    db = SessionLocal()
    try:
        t = Truck(
            truck_type='HCV',
            capacity=15000,
            current_load=0,
            cost_per_km=35.0,
            status='in_transit',
            current_city='Mumbai',
            destination='Pune',
        )
        db.add(t)
        db.flush()

        d = Driver(
            display_name='Hook Test Driver',
            availability_status='on_duty',
            assigned_truck_id=t.truck_id,
            accumulated_driving_minutes=0,
            accumulated_since_last_rest_minutes=0,
        )
        db.add(d)

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
            status='in_transit',
        )
        db.add(s)
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
            status='in_transit',
        )
        db.add(a)
        db.flush()

        h = AssignmentHistory(
            assignment_id=a.assignment_id,
            status='in_transit',
            changed_at=datetime.utcnow() - timedelta(minutes=45),
        )
        db.add(h)
        db.commit()

        ids = {
            'truck': t.truck_id,
            'driver': d.driver_id,
            'shipment': s.load_id,
            'assignment': a.assignment_id,
        }
    finally:
        db.close()
    return ids


def _teardown(ids):
    db = SessionLocal()
    try:
        db.rollback()
    except Exception:
        pass
    try:
        db.query(AssignmentHistory).filter(
            AssignmentHistory.assignment_id == ids['assignment']
        ).delete()
        db.query(Assignment).filter(
            Assignment.assignment_id == ids['assignment']
        ).delete()
        db.query(Driver).filter(
            Driver.driver_id == ids['driver']
        ).delete()
        db.query(Truck).filter(
            Truck.truck_id == ids['truck']
        ).delete()
        db.query(Shipment).filter(
            Shipment.load_id == ids['shipment']
        ).delete()
        db.commit()
    finally:
        db.close()


@patch('backend.api.assignments.reoptimize_fleet')
def test_complete_assignment_includes_driver_update(mock_reopt):
    '''
    Completing an assignment should call apply_completion_to_driver and
    surface the result as 'driver_update' in the response.
    '''
    mock_reopt.return_value = {'optimization': {'assignments': []}}

    ids = _setup_assignment_in_transit()
    try:
        token = _login('admin@fleetops.in', 'admin123')
        url = f"/assignments/{ids['assignment']}/complete"
        r = client.put(url, headers=_hdr(token))
        assert r.status_code == 200, r.text
        body = r.json()

        assert 'driver_update' in body
        du = body['driver_update']
        assert du is not None
        assert du['driver_id'] == ids['driver']
        assert 43 <= du['elapsed_minutes'] <= 47
        assert du['accumulated_driving_minutes'] >= 43
        assert du['rules_verified_against_law'] is False

        assert body['assignment']['status'] == 'completed'
    finally:
        _teardown(ids)


@patch('backend.api.assignments.reoptimize_fleet')
def test_complete_assignment_without_driver_still_succeeds(mock_reopt):
    '''
    A truck with no bound driver must still complete normally.
    driver_update should be None.
    '''
    mock_reopt.return_value = {'optimization': {'assignments': []}}

    db = SessionLocal()
    try:
        t = Truck(
            truck_type='HCV',
            capacity=15000,
            current_load=0,
            cost_per_km=35.0,
            status='in_transit',
            current_city='Mumbai',
            destination='Pune',
        )
        db.add(t)
        db.flush()

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
            status='in_transit',
        )
        db.add(s)
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
            status='in_transit',
        )
        db.add(a)
        db.flush()

        h = AssignmentHistory(
            assignment_id=a.assignment_id,
            status='in_transit',
            changed_at=datetime.utcnow() - timedelta(minutes=20),
        )
        db.add(h)
        db.commit()

        ids = {
            'truck': t.truck_id,
            'shipment': s.load_id,
            'assignment': a.assignment_id,
        }
    finally:
        db.close()

    try:
        token = _login('admin@fleetops.in', 'admin123')
        url = f"/assignments/{ids['assignment']}/complete"
        r = client.put(url, headers=_hdr(token))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get('driver_update') is None
        assert body['assignment']['status'] == 'completed'
    finally:
        db = SessionLocal()
        try:
            db.rollback()
        except Exception:
            pass
        try:
            db.query(AssignmentHistory).filter(
                AssignmentHistory.assignment_id == ids['assignment']
            ).delete()
            db.query(Assignment).filter(
                Assignment.assignment_id == ids['assignment']
            ).delete()
            db.query(Truck).filter(
                Truck.truck_id == ids['truck']
            ).delete()
            db.query(Shipment).filter(
                Shipment.load_id == ids['shipment']
            ).delete()
            db.commit()
        finally:
            db.close()
