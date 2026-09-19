import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.connection import SessionLocal
from backend.models.user import User
from backend.services.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


client = TestClient(app)


# -------------------------------------------------
# Unit: password hashing
# -------------------------------------------------

def test_password_hash_and_verify():
    h = hash_password("secret123")
    assert h != "secret123"
    assert verify_password("secret123", h)
    assert not verify_password("wrong", h)


def test_verify_password_handles_bad_hash():
    assert not verify_password("x", "not-a-real-hash")


# -------------------------------------------------
# Unit: tokens
# -------------------------------------------------

def test_access_and_refresh_token_types():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@fleetops.in").first()
        assert user is not None, "Seed users first: python -m scripts.seed_users"

        access = create_access_token(user)
        refresh = create_refresh_token(user)

        a_payload = decode_token(access, expected_type="access")
        r_payload = decode_token(refresh, expected_type="refresh")

        assert a_payload["sub"] == str(user.user_id)
        assert a_payload["type"] == "access"
        assert r_payload["type"] == "refresh"
    finally:
        db.close()


def test_decode_wrong_token_type_raises():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@fleetops.in").first()
        access = create_access_token(user)

        with pytest.raises(Exception):
            decode_token(access, expected_type="refresh")
    finally:
        db.close()


# -------------------------------------------------
# Integration: routes
# -------------------------------------------------

def test_login_success_returns_tokens():
    resp = client.post(
        "/auth/login",
        json={"email": "admin@fleetops.in", "password": "admin123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == "admin@fleetops.in"
    assert body["user"]["role"] == "admin"


def test_login_wrong_password():
    resp = client.post(
        "/auth/login",
        json={"email": "admin@fleetops.in", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_me_requires_auth():
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token():
    login = client.post(
        "/auth/login",
        json={"email": "manager@fleetops.in", "password": "manager123"},
    )
    token = login.json()["access_token"]

    resp = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "manager@fleetops.in"


def test_me_with_invalid_token():
    resp = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert resp.status_code == 401


def test_refresh_flow():
    login = client.post(
        "/auth/login",
        json={"email": "admin@fleetops.in", "password": "admin123"},
    )
    refresh_token = login.json()["refresh_token"]

    resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_health_is_public():
    resp = client.get("/health")
    assert resp.status_code == 200
