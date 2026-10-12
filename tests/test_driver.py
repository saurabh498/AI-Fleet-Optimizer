'''Driver entity and feasibility tests.'''

from fastapi.testclient import TestClient

from backend.database.connection import SessionLocal
from backend.main import app
from backend.models.driver import Driver
from backend.models.truck import Truck
from backend.services.driver_feasibility import (
    check_driver_feasibility,
    get_rule,
    is_rules_verified,
)


client = TestClient(app)


def _login(email, password):
    r = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _hdr(token):
    return {"Authorization": f"Bearer {token}"}


# -------------------------------------------------
# Config sanity
# -------------------------------------------------

def test_rules_are_explicitly_unverified():
    '''Rules MUST default to unverified until reviewed.'''
    assert is_rules_verified() is False


def test_rules_have_required_keys():
    for key in (
        "max_continuous_driving_minutes",
        "min_rest_duration_minutes",
        "max_daily_driving_minutes",
    ):
        assert get_rule(key) is not None


# -------------------------------------------------
# Feasibility (unit)
# -------------------------------------------------

def _mock_truck():
    truck = Truck(
        truck_id=999,
        truck_type='HCV',
        capacity=15000,
        cost_per_km=35.0,
    )
    return truck


def test_missing_driver_requires_review():
    r = check_driver_feasibility(None, _mock_truck(), 60)
    assert r['feasible'] is False
    assert r['requires_review'] is True


def test_off_duty_driver_blocked():
    d = Driver(
        driver_id=1,
        display_name='X',
        availability_status='off_duty',
    )
    r = check_driver_feasibility(d, _mock_truck(), 60)
    assert r['feasible'] is False
    assert 'off_duty' in r['reason']


def test_rest_required_blocks():
    d = Driver(
        driver_id=1,
        display_name='X',
        availability_status='available',
        rest_required=True,
    )
    r = check_driver_feasibility(d, _mock_truck(), 60)
    assert r['feasible'] is False
    assert 'rest' in r['reason'].lower()


def test_truck_conflict_blocks():
    d = Driver(
        driver_id=1,
        display_name='X',
        availability_status='available',
        assigned_truck_id=42,
    )
    r = check_driver_feasibility(d, _mock_truck(), 60)
    assert r['feasible'] is False
    assert 'assigned to truck' in r['reason'].lower()


def test_missing_accumulated_data_requires_review():
    d = Driver(
        driver_id=1,
        display_name='X',
        availability_status='available',
        accumulated_driving_minutes=None,
        accumulated_since_last_rest_minutes=None,
    )
    r = check_driver_feasibility(d, _mock_truck(), 30)
    assert r['feasible'] is False
    assert r['requires_review'] is True
    assert len(r['missing_data']) >= 1


def test_clean_driver_passes_but_flags_review():
    d = Driver(
        driver_id=1,
        display_name='X',
        availability_status='available',
        accumulated_driving_minutes=60,
        accumulated_since_last_rest_minutes=60,
    )
    r = check_driver_feasibility(d, _mock_truck(), 60)
    assert r['feasible'] is True
    # Rules unverified -> review still required
    assert r['requires_review'] is True


def test_continuous_driving_limit_triggers_review():
    max_c = get_rule('max_continuous_driving_minutes')
    d = Driver(
        driver_id=1,
        display_name='X',
        availability_status='available',
        accumulated_driving_minutes=0,
        accumulated_since_last_rest_minutes=max_c,
    )
    r = check_driver_feasibility(d, _mock_truck(), 30)
    assert r['feasible'] is False
    assert 'continuous' in r['reason'].lower()


# -------------------------------------------------
# RBAC (integration)
# -------------------------------------------------

def test_list_drivers_requires_auth():
    r = client.get('/drivers/')
    assert r.status_code in (401, 403)


def test_driver_role_cannot_create():
    token = _login('driver@fleetops.in', 'driver123')
    r = client.post(
        '/drivers/',
        json={'display_name': 'X'},
        headers=_hdr(token),
    )
    assert r.status_code == 403


def test_manager_can_create_and_delete():
    token = _login('manager@fleetops.in', 'manager123')
    r = client.post(
        '/drivers/',
        json={'display_name': 'Test Driver Stage1'},
        headers=_hdr(token),
    )
    assert r.status_code == 201, r.text
    new_id = r.json()['driver_id']

    # cleanup
    r2 = client.delete(f'/drivers/{new_id}', headers=_hdr(token))
    assert r2.status_code == 200
