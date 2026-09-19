"""
Fleet-wide GPS simulator with authentication.

Logs in as the admin user at start, then drives every
in_transit assignment through its route, sending GPS
points and letting the backend auto-detect arrival.

Env vars (all optional):
    SIM_BASE_URL    default http://127.0.0.1:8000
    SIM_EMAIL       default admin@fleetops.in
    SIM_PASSWORD    default admin123
    SIM_STEPS       default 10
    SIM_INTERVAL    default 2 (seconds)

Usage (from repo root):
    python -m simulator.gps_simulator
or:
    python simulator/gps_simulator.py
"""

import os
import threading
import time
from datetime import datetime

import requests


BASE_URL = os.getenv("SIM_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SIM_EMAIL = os.getenv("SIM_EMAIL", "admin@fleetops.in")
SIM_PASSWORD = os.getenv("SIM_PASSWORD", "admin123")

STEPS = int(os.getenv("SIM_STEPS", "10"))
INTERVAL_SECONDS = float(os.getenv("SIM_INTERVAL", "2"))

AUTH_HEADERS = {}


# -------------------------------------------------
# Auth
# -------------------------------------------------

def login():
    """Authenticate and store the bearer token globally."""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": SIM_EMAIL, "password": SIM_PASSWORD},
        timeout=10,
    )
    response.raise_for_status()
    token = response.json()["access_token"]
    AUTH_HEADERS["Authorization"] = f"Bearer {token}"
    print(f"Authenticated as {SIM_EMAIL}")


def _auth_get(path):
    response = requests.get(
        f"{BASE_URL}{path}",
        headers=AUTH_HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _auth_post(path, payload):
    response = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        headers=AUTH_HEADERS,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


# -------------------------------------------------
# Data fetchers
# -------------------------------------------------

def get_truck(truck_id):
    return _auth_get(f"/trucks/{truck_id}")


def get_shipment(load_id):
    return _auth_get(f"/shipments/{load_id}")


def get_all_assignments():
    return _auth_get("/assignments/")


def get_in_transit_assignments():
    return [
        a for a in get_all_assignments()
        if a.get("status") == "in_transit"
    ]


def send_location(truck_id, latitude, longitude, speed):
    return _auth_post(
        "/locations/",
        {
            "truck_id": truck_id,
            "timestamp": datetime.now().isoformat(),
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "speed": speed,
        },
    )


def check_arrival(assignment_id):
    return _auth_get(f"/assignments/{assignment_id}/arrival")


# -------------------------------------------------
# Logging
# -------------------------------------------------

def log(truck_id, message):
    print(f"[Truck {truck_id}] {message}")


# -------------------------------------------------
# Movement
# -------------------------------------------------

def move_truck_through_route(
    truck_id,
    assignment_id,
    load_id,
    start_latitude,
    start_longitude,
    pickup_latitude,
    pickup_longitude,
    destination_latitude,
    destination_longitude,
):
    # Stage 1: current -> pickup
    pickup_steps = max(STEPS // 2, 1)
    lat_step = (pickup_latitude - start_latitude) / pickup_steps
    lon_step = (pickup_longitude - start_longitude) / pickup_steps

    for step in range(pickup_steps + 1):
        latitude = start_latitude + lat_step * step
        longitude = start_longitude + lon_step * step
        speed = 0 if step == pickup_steps else 60

        try:
            location = send_location(truck_id, latitude, longitude, speed)
            log(
                truck_id,
                f"[PICKUP {step:02d}/{pickup_steps}] "
                f"Lat: {location['latitude']:.4f} | "
                f"Lon: {location['longitude']:.4f} | "
                f"Speed: {location['speed']} km/h",
            )
        except requests.RequestException as error:
            log(truck_id, f"GPS update failed: {error}")
            return

        if step < pickup_steps:
            time.sleep(INTERVAL_SECONDS)

    # Stage 2: pickup -> destination
    lat_step = (destination_latitude - pickup_latitude) / STEPS
    lon_step = (destination_longitude - pickup_longitude) / STEPS

    for step in range(STEPS + 1):
        latitude = pickup_latitude + lat_step * step
        longitude = pickup_longitude + lon_step * step
        speed = 0 if step == STEPS else 60

        try:
            location = send_location(truck_id, latitude, longitude, speed)
            log(
                truck_id,
                f"[DEST {step:02d}/{STEPS}] "
                f"Lat: {location['latitude']:.4f} | "
                f"Lon: {location['longitude']:.4f} | "
                f"Speed: {location['speed']} km/h",
            )
        except requests.RequestException as error:
            log(truck_id, f"GPS update failed: {error}")
            return

        if step < STEPS:
            time.sleep(INTERVAL_SECONDS)

    # Arrival check
    try:
        arrival_result = check_arrival(assignment_id)

        if arrival_result.get("arrival", {}).get("arrived"):
            completion = arrival_result.get("completion", {})
            reopt = completion.get("reoptimization", {})
            log(truck_id, "ARRIVED - assignment auto-completed")
            log(truck_id, f"Fleet re-optimization: {reopt.get('message')}")
        else:
            distance = arrival_result.get("distance_to_destination_km")
            log(truck_id, f"Not yet arrived - {distance} km remaining")

    except requests.RequestException as error:
        log(truck_id, f"Arrival check failed: {error}")


def simulate_truck(assignment):
    truck_id = assignment["truck_id"]
    assignment_id = assignment["assignment_id"]
    load_id = assignment["load_id"]

    try:
        truck = get_truck(truck_id)
        shipment = get_shipment(load_id)
    except requests.RequestException as error:
        log(truck_id, f"Failed to load truck/shipment data: {error}")
        return

    if truck["current_latitude"] is None or truck["current_longitude"] is None:
        log(truck_id, "Skipped - truck has no current location")
        return

    log(
        truck_id,
        f"Starting route: {shipment['pickup_city']} -> "
        f"{shipment['destination_city']} (assignment #{assignment_id})",
    )

    move_truck_through_route(
        truck_id=truck_id,
        assignment_id=assignment_id,
        load_id=load_id,
        start_latitude=truck["current_latitude"],
        start_longitude=truck["current_longitude"],
        pickup_latitude=shipment["pickup_latitude"],
        pickup_longitude=shipment["pickup_longitude"],
        destination_latitude=shipment["destination_latitude"],
        destination_longitude=shipment["destination_longitude"],
    )


# -------------------------------------------------
# Entry point
# -------------------------------------------------

def simulate_fleet():
    print("=" * 60)
    print("AI FLEET OPTIMIZER - MULTI-TRUCK GPS SIMULATOR")
    print("=" * 60)

    try:
        login()
    except requests.RequestException as error:
        print(f"Login failed: {error}")
        print("Is the backend running on", BASE_URL, "?")
        return

    in_transit = get_in_transit_assignments()

    if not in_transit:
        print()
        print("No in_transit assignments found.")
        print("Start one or more assignments first (PUT /assignments/{id}/start).")
        return

    print(f"Found {len(in_transit)} truck(s) in transit:")
    for assignment in in_transit:
        print(
            f"  - Truck {assignment['truck_id']} "
            f"(assignment #{assignment['assignment_id']}, "
            f"load #{assignment['load_id']})"
        )
    print("=" * 60)
    print()

    threads = [
        threading.Thread(target=simulate_truck, args=(assignment,))
        for assignment in in_transit
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print()
    print("=" * 60)
    print("Fleet GPS simulation completed.")
    print("=" * 60)


if __name__ == "__main__":
    simulate_fleet()
