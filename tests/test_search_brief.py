'''External search brief endpoint tests.'''

from fastapi.testclient import TestClient

from backend.database.connection import SessionLocal
from backend.main import app
from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation


client = TestClient(app)


def _login(email, password):
    r = client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _hdr(token):
    return {"Authorization": "Bearer " + token}


def _make_truck(db, city="Mumbai", status="available"):
    t = Truck(
        truck_type="HCV",
        capacity=15000,
        current_load=0,
        cost_per_km=35.0,
        status=status,
        current_city=city,
        current_latitude=19.0760,
        current_longitude=72.8777,
    )
    db.add(t)
    db.flush()
    return t


def _cleanup(truck_id):
    db = SessionLocal()
    try:
        db.rollback()
    except Exception:
        pass
    try:
        db.query(TruckLocation).filter(
            TruckLocation.truck_id == truck_id
        ).delete()
        db.query(Truck).filter(Truck.truck_id == truck_id).delete()
        db.commit()
    finally:
        db.close()


# -------------------------------------------------
# Happy path
# -------------------------------------------------

def test_generate_brief_for_available_truck():
    db = SessionLocal()
    t = _make_truck(db)
    db.commit()
    truck_id = t.truck_id
    db.close()

    try:
        token = _login("admin@fleetops.in", "admin123")
        r = client.post(
            "/search-brief/" + str(truck_id), headers=_hdr(token)
        )
        assert r.status_code == 200, r.text
        body = r.json()

        assert body["truck_id"] == truck_id
        assert body["brief"]["truck_type"] == "HCV"
        assert body["brief"]["capacity_kg"] == 15000
        assert body["brief"]["current_city"] == "Mumbai"
        assert body["brief"]["availability"] == "Available now"
        assert "generated_text" in body
        assert "generated_at" in body
        assert "internal_search_summary" in body
        assert "external_search_recommended" in body
    finally:
        _cleanup(truck_id)


def test_brief_text_contains_required_sections():
    db = SessionLocal()
    t = _make_truck(db)
    db.commit()
    truck_id = t.truck_id
    db.close()

    try:
        token = _login("admin@fleetops.in", "admin123")
        r = client.post(
            "/search-brief/" + str(truck_id), headers=_hdr(token)
        )
        text = r.json()["generated_text"]

        assert "RETURN LOAD ENQUIRY" in text
        assert "TRUCK" in text
        assert "LOCATION & AVAILABILITY" in text
        assert "PREFERRED ROUTES" in text
        assert "CARGO CONSTRAINTS" in text
        assert "INTERNAL SEARCH SUMMARY" in text
        assert "PRIVACY" in text
    finally:
        _cleanup(truck_id)


# -------------------------------------------------
# Privacy checks
# -------------------------------------------------

def test_brief_text_does_not_leak_internal_ids():
    db = SessionLocal()
    t = _make_truck(db)
    db.commit()
    truck_id = t.truck_id
    db.close()

    try:
        token = _login("admin@fleetops.in", "admin123")
        r = client.post(
            "/search-brief/" + str(truck_id), headers=_hdr(token)
        )
        text = r.json()["generated_text"]

        # Text should NOT contain the internal truck_id
        assert ("Truck #" + str(truck_id)) not in text
        assert ("truck_id=" + str(truck_id)) not in text
    finally:
        _cleanup(truck_id)


def test_privacy_note_is_present():
    db = SessionLocal()
    t = _make_truck(db)
    db.commit()
    truck_id = t.truck_id
    db.close()

    try:
        token = _login("admin@fleetops.in", "admin123")
        r = client.post(
            "/search-brief/" + str(truck_id), headers=_hdr(token)
        )
        body = r.json()
        assert "driver" in body["privacy_note"].lower()
        assert "registration" in body["privacy_note"].lower()
    finally:
        _cleanup(truck_id)


# -------------------------------------------------
# Error cases
# -------------------------------------------------

def test_missing_truck_returns_404():
    token = _login("admin@fleetops.in", "admin123")
    r = client.post(
        "/search-brief/999999", headers=_hdr(token)
    )
    assert r.status_code == 404


# -------------------------------------------------
# RBAC
# -------------------------------------------------

def test_requires_auth():
    r = client.post("/search-brief/1")
    assert r.status_code in (401, 403)


def test_driver_role_can_read_brief():
    '''Drivers can generate a brief too - it is read-only.'''
    db = SessionLocal()
    t = _make_truck(db)
    db.commit()
    truck_id = t.truck_id
    db.close()

    try:
        token = _login("driver@fleetops.in", "driver123")
        r = client.post(
            "/search-brief/" + str(truck_id), headers=_hdr(token)
        )
        assert r.status_code == 200
    finally:
        _cleanup(truck_id)
