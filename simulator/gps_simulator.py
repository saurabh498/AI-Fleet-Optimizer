import time
from datetime import datetime

import requests


BASE_URL = "http://127.0.0.1:8000"

TRUCK_ID = 1

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


def check_arrival(assignment_id):
    """
    Check whether the truck has reached
    the shipment destination.

    If arrived, the backend automatically:
    - completes the assignment
    - marks shipment as delivered
    - makes truck available
    - triggers fleet re-optimization
    """

    response = requests.get(
        f"{BASE_URL}/assignments/{assignment_id}/arrival",
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

    assignment_id = assignment["assignment_id"]
    load_id = assignment["load_id"]
    assignment_status = assignment["status"]

    print(f"Assignment ID  : {assignment_id}")
    print(f"Load ID        : {load_id}")
    print(f"Assignment     : {assignment_status}")

    # GPS simulation is allowed only for in_transit
    if assignment_status != "in_transit":
        print()
        print("=" * 60)
        print("GPS SIMULATION BLOCKED")
        print("=" * 60)
        print(f"Assignment Status : {assignment_status}")
        print("Required Status   : in_transit")
        print(
            "Reason            : "
            "GPS simulation can only run for active transit assignments."
        )
        print("=" * 60)
        return

    # -------------------------------------------------
    # 3. Get shipment
    # -------------------------------------------------

    shipment = get_shipment(load_id)

    truck_latitude = truck["current_latitude"]
    truck_longitude = truck["current_longitude"]

    pickup_latitude = shipment["pickup_latitude"]
    pickup_longitude = shipment["pickup_longitude"]

    destination_latitude = shipment["destination_latitude"]
    destination_longitude = shipment["destination_longitude"]

    print(
        f"Truck Location : "
        f"{truck_latitude}, "
        f"{truck_longitude}"
    )

    print(
        f"Pickup         : "
        f"{pickup_latitude}, "
        f"{pickup_longitude}"
    )

    print(
        f"Destination    : "
        f"{destination_latitude}, "
        f"{destination_longitude}"
    )

    print(
        f"Route          : "
        f"{shipment['pickup_city']} -> "
        f"{shipment['destination_city']}"
    )

    print(f"GPS Updates    : {STEPS}")
    print(f"Interval       : {INTERVAL_SECONDS} seconds")
    print("=" * 60)

    simulation_success = True

    # -------------------------------------------------
    # 4. STAGE 1
    # Truck -> Pickup
    # -------------------------------------------------

    pickup_steps = max(STEPS // 2, 1)

    pickup_latitude_step = (
        pickup_latitude - truck_latitude
    ) / pickup_steps

    pickup_longitude_step = (
        pickup_longitude - truck_longitude
    ) / pickup_steps

    print()
    print("=" * 60)
    print("STAGE 1: MOVING TO PICKUP")
    print("=" * 60)

    for step in range(pickup_steps + 1):

        latitude = (
            truck_latitude
            + pickup_latitude_step * step
        )

        longitude = (
            truck_longitude
            + pickup_longitude_step * step
        )

        speed = 0 if step == pickup_steps else 60

        try:

            location = send_location(
                latitude,
                longitude,
                speed
            )

            print(
                f"[PICKUP {step:02d}/{pickup_steps}] "
                f"Lat: {location['latitude']:.6f} | "
                f"Lon: {location['longitude']:.6f} | "
                f"Speed: {location['speed']} km/h | "
                f"Location ID: {location['location_id']}"
            )

        except requests.RequestException as error:

            print(
                f"GPS update failed: {error}"
            )

            simulation_success = False
            break

        if step < pickup_steps:
            time.sleep(INTERVAL_SECONDS)

    # -------------------------------------------------
    # 5. STAGE 2
    # Pickup -> Destination
    # -------------------------------------------------

    if simulation_success:

        destination_steps = STEPS

        destination_latitude_step = (
            destination_latitude - pickup_latitude
        ) / destination_steps

        destination_longitude_step = (
            destination_longitude - pickup_longitude
        ) / destination_steps

        print()
        print("=" * 60)
        print("STAGE 2: MOVING TO DESTINATION")
        print("=" * 60)

        for step in range(destination_steps + 1):

            latitude = (
                pickup_latitude
                + destination_latitude_step * step
            )

            longitude = (
                pickup_longitude
                + destination_longitude_step * step
            )

            speed = 0 if step == destination_steps else 60

            try:

                location = send_location(
                    latitude,
                    longitude,
                    speed
                )

                print(
                    f"[DEST {step:02d}/{destination_steps}] "
                    f"Lat: {location['latitude']:.6f} | "
                    f"Lon: {location['longitude']:.6f} | "
                    f"Speed: {location['speed']} km/h | "
                    f"Location ID: {location['location_id']}"
                )

            except requests.RequestException as error:

                print(
                    f"GPS update failed: {error}"
                )

                simulation_success = False
                break

            if step < destination_steps:
                time.sleep(INTERVAL_SECONDS)

    # -------------------------------------------------
    # 6. Automatic arrival detection
    # -------------------------------------------------

    if simulation_success:

        print()
        print("=" * 60)
        print("CHECKING AUTOMATIC ARRIVAL...")
        print("=" * 60)

        try:

            arrival_result = check_arrival(
                assignment_id
            )

            if arrival_result.get(
                "arrival",
                {}
            ).get("arrived"):

                print()
                print("=" * 60)
                print("AUTOMATIC ARRIVAL DETECTED")
                print("=" * 60)

                completion = arrival_result.get(
                    "completion",
                    {}
                )

                assignment_result = completion.get(
                    "assignment",
                    {}
                )

                truck_result = completion.get(
                    "truck",
                    {}
                )

                shipment_result = completion.get(
                    "shipment",
                    {}
                )

                print(
                    "Assignment Status :",
                    assignment_result.get("status")
                )

                print(
                    "Truck Status      :",
                    truck_result.get("status")
                )

                print(
                    "Truck Load        :",
                    truck_result.get("current_load")
                )

                print(
                    "Truck Destination :",
                    truck_result.get("destination")
                )

                print(
                    "Shipment Status   :",
                    shipment_result.get("status")
                )

                reoptimization = completion.get(
                    "reoptimization",
                    {}
                )

                print()
                print(
                    "Fleet Re-optimization:",
                    reoptimization.get("message")
                )

                print("=" * 60)
                print(
                    "Assignment automatically completed."
                )
                print("=" * 60)

            else:

                print()
                print(
                    "Truck has not reached the destination."
                )

                print(
                    "Distance to destination:",
                    arrival_result.get(
                        "distance_to_destination_km"
                    ),
                    "km"
                )

        except requests.RequestException as error:

            print(
                "Automatic arrival check failed:",
                error
            )

    print()
    print("=" * 60)
    print("Assignment GPS simulation completed.")
    print("=" * 60)

if __name__ == "__main__":
    simulate_assignment_movement()    