'''
Verify role-based access control on fleet routes.
'''

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _login(email: str, password: str) -> str:
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _hdr(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# -------------------------------------------------
# Anonymous access
# -------------------------------------------------

def test_create_truck_without_token_is_blocked():
    resp = client.post(
        "/trucks/",
        json={
            "truck_type": "HCV",
            "capacity": 15000,
            "current_load": 0,
            "current_city": "Mumbai",
            "status": "available",
            "cost_per_km": 35.0,
        },
    )
    # Either 401 (auth middleware) or 403 (dependency)
    assert resp.status_code in (401, 403)


def test_delete_shipment_without_token_is_blocked():
    resp = client.delete("/shipments/1")
    assert resp.status_code in (401, 403)


# -------------------------------------------------
# Driver cannot write
# -------------------------------------------------

def test_driver_cannot_create_truck():
    token = _login("driver@fleetops.in", "driver123")
    resp = client.post(
        "/trucks/",
        json={
            "truck_type": "HCV",
            "capacity": 15000,
            "current_load": 0,
            "current_city": "Mumbai",
            "status": "available",
            "cost_per_km": 35.0,
        },
        headers=_hdr(token),
    )
    assert resp.status_code == 403


def test_driver_cannot_create_shipment():
    token = _login("driver@fleetops.in", "driver123")
    resp = client.post(
        "/shipments/",
        json={
            "pickup_city": "Mumbai",
            "pickup_latitude": 19.0760,
            "pickup_longitude": 72.8777,
            "destination_city": "Pune",
            "destination_latitude": 18.5204,
            "destination_longitude": 73.8567,
            "weight": 5000,
            "cargo_type": "Electronics",
            "revenue": 20000,
            "status": "available",
        },
        headers=_hdr(token),
    )
    assert resp.status_code == 403


# -------------------------------------------------
# Manager can write
# -------------------------------------------------

def test_manager_can_create_truck():
    token = _login("manager@fleetops.in", "manager123")
    resp = client.post(
        "/trucks/",
        json={
            "truck_type": "LCV",
            "capacity": 5000,
            "current_load": 0,
            "current_city": "Pune",
            "status": "available",
            "cost_per_km": 22.0,
        },
        headers=_hdr(token),
    )
    assert resp.status_code in (200, 201), resp.text

    # Cleanup
    truck_id = resp.json()["truck_id"]
    client.delete(
        f"/trucks/{truck_id}",
        headers=_hdr(token),
    )


def test_admin_can_create_truck():
    token = _login("admin@fleetops.in", "admin123")
    resp = client.post(
        "/trucks/",
        json={
            "truck_type": "HCV",
            "capacity": 18000,
            "current_load": 0,
            "current_city": "Delhi",
            "status": "available",
            "cost_per_km": 38.0,
        },
        headers=_hdr(token),
    )
    assert resp.status_code in (200, 201), resp.text

    truck_id = resp.json()["truck_id"]
    client.delete(f"/trucks/{truck_id}", headers=_hdr(token))


# -------------------------------------------------
# Reads now require authentication
# -------------------------------------------------

def test_get_trucks_requires_auth():
    resp = client.get("/trucks/")
    assert resp.status_code in (401, 403)


def test_get_shipments_requires_auth():
    resp = client.get("/shipments/")
    assert resp.status_code in (401, 403)


def test_get_assignments_requires_auth():
    resp = client.get("/assignments/")
    assert resp.status_code in (401, 403)


def test_get_backhaul_decision_requires_auth():
    resp = client.get("/backhaul/decision/1")
    assert resp.status_code in (401, 403)


def test_driver_can_read_trucks():
    token = _login("driver@fleetops.in", "driver123")
    resp = client.get("/trucks/", headers=_hdr(token))
    assert resp.status_code == 200


def test_manager_can_read_shipments():
    token = _login("manager@fleetops.in", "manager123")
    resp = client.get("/shipments/", headers=_hdr(token))
    assert resp.status_code == 200


def test_admin_can_read_backhaul_decision():
    token = _login("admin@fleetops.in", "admin123")
    resp = client.get("/backhaul/decision/1", headers=_hdr(token))
    assert resp.status_code == 200
