import time
from datetime import datetime

import requests


BASE_URL = "http://127.0.0.1:8000"

TRUCK_ID = 2

STEPS = 10
INTERVAL_SECONDS = 2


def get_truck():
    response = requests.get(
        f"{BASE_URL}/trucks/{TRUCK_ID}",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def get_active_assignment():
    response = requests.get(
        f"{BASE_URL}/assignments/",
        timeout=10
    )

    response.raise_for_status()

    assignments = response.json()

    active_statuses = ["assigned", "in_transit"]

    for assignment in assignments:
        if (
            assignment.get("truck_id") == TRUCK_ID
            and assignment.get("status") in active_statuses
        ):
            return assignment

    return None


def get_shipment(load_id):
    response = requests.get(
        f"{BASE_URL}/shipments/{load_id}",
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def send_location(
    latitude,
    longitude,
    speed
):
    payload = {
        "truck_id": TRUCK_ID,
        "timestamp": datetime.now().isoformat(),
        "latitude": round(latitude, 6),
        "longitude": round(longitude, 6),
        "speed": speed
    }

    response = requests.post(
        f"{BASE_URL}/locations/",
        json=payload,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def simulate_assignment_movement():

    print("=" * 60)
    print("AI FLEET OPTIMIZER - ASSIGNMENT GPS SIMULATOR")
    print("=" * 60)

    # -------------------------------------------------
    # 1. Get truck
    # -------------------------------------------------

    truck = get_truck()

    print(f"Truck ID       : {truck['truck_id']}")
    print(f"Truck Status   : {truck['status']}")
    print(
        f"Current GPS    : "
        f"{truck['current_latitude']}, "
        f"{truck['current_longitude']}"
    )

    # -------------------------------------------------
    # 2. Find active assignment
    # -------------------------------------------------

    assignment = get_active_assignment()

    if assignment is None:
        print()
        print("ERROR: No active assignment found for this truck.")
        print("Create and start an assignment before running the simulator.")
        return

    load_id = assignment["load_id"]

    print(f"Assignment ID  : {assignment['assignment_id']}")
    print(f"Load ID        : {load_id}")
    print(f"Assignment     : {assignment['status']}")

    # -------------------------------------------------
    # 3. Get shipment
    # -------------------------------------------------

    shipment = get_shipment(load_id)

    start_latitude = truck["current_latitude"]
    start_longitude = truck["current_longitude"]

    destination_latitude = shipment["destination_latitude"]
    destination_longitude = shipment["destination_longitude"]

    print(
        f"Route          : "
        f"{shipment['pickup_city']} -> "
        f"{shipment['destination_city']}"
    )

    print(
        f"Destination    : "
        f"{destination_latitude}, "
        f"{destination_longitude}"
    )

    print(f"GPS Updates    : {STEPS}")
    print(f"Interval       : {INTERVAL_SECONDS} seconds")
    print("=" * 60)

    # -------------------------------------------------
    # 4. Calculate movement
    # -------------------------------------------------

    latitude_step = (
        destination_latitude - start_latitude
    ) / STEPS

    longitude_step = (
        destination_longitude - start_longitude
    ) / STEPS

    # -------------------------------------------------
    # 5. Simulate movement
    # -------------------------------------------------

    for step in range(STEPS + 1):

        latitude = (
            start_latitude
            + latitude_step * step
        )

        longitude = (
            start_longitude
            + longitude_step * step
        )

        if step == STEPS:
            speed = 0
        else:
            speed = 60

        try:
            location = send_location(
                latitude,
                longitude,
                speed
            )

            print(
                f"[{step:02d}/{STEPS}] "
                f"Lat: {location['latitude']:.6f} | "
                f"Lon: {location['longitude']:.6f} | "
                f"Speed: {location['speed']} km/h | "
                f"Location ID: {location['location_id']}"
            )

        except requests.RequestException as error:
            print(f"GPS update failed: {error}")
            break

        if step < STEPS:
            time.sleep(INTERVAL_SECONDS)

    print("=" * 60)
    print("Assignment GPS simulation completed.")
    print("=" * 60)


if __name__ == "__main__":
    simulate_assignment_movement()