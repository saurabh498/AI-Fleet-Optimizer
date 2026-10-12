"""
External search brief generator.

When the internal backhaul search finds no viable shipment, this
service produces a structured brief the fleet manager can copy into
an external load board search form (BlackBuck, Vahak, etc.).

It does NOT call any external API. This is an assisted-manual
workflow by design: nothing is auto-transmitted, and no third-party
integration is claimed.

Privacy: the generated text never includes driver name, vehicle
registration, internal IDs, or customer-identifying details.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.truck import Truck
from backend.models.truck_location import TruckLocation
from backend.services.backhaul_matching import find_backhaul_matches


FEASIBLE_EFFICIENCY_MIN = 40
FEASIBLE_PROFIT_MIN = 0


def _latest_position(truck, db):
    """Return (lat, lon, source). Latest GPS location is authoritative."""
    location = (
        db.query(TruckLocation)
        .filter(TruckLocation.truck_id == truck.truck_id)
        .order_by(TruckLocation.timestamp.desc())
        .first()
    )
    if location is not None:
        return (location.latitude, location.longitude, "latest_gps")
    if (
        truck.current_latitude is not None
        and truck.current_longitude is not None
    ):
        return (
            truck.current_latitude,
            truck.current_longitude,
            "truck_record",
        )
    return (None, None, "unavailable")


def _availability_text(truck):
    if truck.status == "available":
        return "Available now"
    if truck.status == "waiting":
        return "Waiting at current location"
    if truck.status == "assigned":
        return "Assigned - enquire for release time"
    if truck.status == "in_transit":
        return "In transit - enquire for arrival time"
    return "Status unknown - confirm with operator"


def _preferred_routes(matches, limit):
    routes = []
    for m in matches[:limit]:
        route = m.get("route") or {}
        routes.append({
            "pickup_city": m.get("pickup_city"),
            "destination_city": m.get("destination_city"),
            "distance_km": route.get("total_distance_km"),
            "match_score": m.get("match_score"),
            "route_efficiency_score": m.get("route_efficiency_score"),
        })
    return routes


def _build_text(brief):
    b = brief["brief"]
    s = brief["internal_search_summary"]

    lines = []
    lines.append("=== RETURN LOAD ENQUIRY ===")
    lines.append("")

    lines.append("TRUCK")
    lines.append("  Type: " + str(b["truck_type"]))
    lines.append(
        "  Capacity: " + "{:,}".format(int(b["capacity_kg"])) + " kg"
    )
    lines.append(
        "  Current load: "
        + "{:,}".format(int(b["current_load_kg"]))
        + " kg"
    )
    lines.append(
        "  Remaining capacity: "
        + "{:,}".format(int(b["remaining_capacity_kg"]))
        + " kg"
    )
    lines.append("")

    lines.append("LOCATION & AVAILABILITY")
    if b["current_city"]:
        lines.append("  Current city: " + str(b["current_city"]))
    if (
        b["current_latitude"] is not None
        and b["current_longitude"] is not None
    ):
        lines.append(
            "  Position: "
            + "{:.4f}".format(float(b["current_latitude"]))
            + "N, "
            + "{:.4f}".format(float(b["current_longitude"]))
            + "E"
        )
    lines.append("  Availability: " + str(b["availability"]))
    lines.append("")

    lines.append("PREFERRED ROUTES")
    if b["preferred_routes"]:
        for i, r in enumerate(b["preferred_routes"], start=1):
            line = (
                "  "
                + str(i)
                + ". "
                + str(r["pickup_city"])
                + " -> "
                + str(r["destination_city"])
            )
            if r["distance_km"] is not None:
                line += (
                    "  (~"
                    + "{:.0f}".format(float(r["distance_km"]))
                    + " km)"
                )
            lines.append(line)
    else:
        lines.append("  No specific destination preference.")
        lines.append("  Open to any direction with suitable cargo.")
    lines.append("")

    lines.append("CARGO CONSTRAINTS")
    lines.append(
        "  Maximum weight: "
        + "{:,}".format(int(b["max_weight_kg"]))
        + " kg"
    )
    lines.append("  Suitable cargo types: general cargo, no hazmat")
    lines.append("")

    lines.append("INTERNAL SEARCH SUMMARY")
    lines.append(
        "  Candidates evaluated: " + str(s["candidates_considered"])
    )
    lines.append(
        "  Feasible matches found: " + str(s["feasible_matches"])
    )
    if s["feasible_matches"] == 0:
        lines.append(
            "  Outcome: no suitable internal shipment - external search requested"
        )
    else:
        lines.append(
            "  Outcome: internal matches exist - external search secondary"
        )
    lines.append("")

    lines.append("NEXT STEPS")
    lines.append(
        "  Paste this brief into an external load board search form."
    )
    lines.append(
        "  This system does NOT auto-transmit to external platforms."
    )
    lines.append("")

    lines.append("PRIVACY")
    lines.append(
        "  Driver name, vehicle registration, and customer details"
    )
    lines.append("  are intentionally excluded from this brief.")

    return "\n".join(lines)


def generate_search_brief(truck_id, db, max_preferred_routes=3):
    truck = db.query(Truck).filter(Truck.truck_id == truck_id).first()
    if truck is None:
        return None

    lat, lon, source = _latest_position(truck, db)

    matches_result = find_backhaul_matches(truck_id, db)
    matches = (matches_result or {}).get("matches", []) or []

    feasible = [
        m
        for m in matches
        if (m.get("route_efficiency_score") or 0) >= FEASIBLE_EFFICIENCY_MIN
        and (m.get("estimated_route_profit") or 0) > FEASIBLE_PROFIT_MIN
    ]

    capacity = float(truck.capacity or 0)
    current_load = float(truck.current_load or 0)
    remaining = max(0.0, capacity - current_load)

    brief = {
        "truck_id": truck_id,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "internal_search_summary": {
            "candidates_considered": len(matches),
            "feasible_matches": len(feasible),
            "best_match_available": len(matches) > 0,
        },
        "external_search_recommended": len(feasible) == 0,
        "brief": {
            "truck_type": truck.truck_type,
            "capacity_kg": capacity,
            "current_load_kg": current_load,
            "remaining_capacity_kg": remaining,
            "current_city": truck.current_city,
            "current_latitude": lat,
            "current_longitude": lon,
            "position_source": source,
            "availability": _availability_text(truck),
            "preferred_routes": _preferred_routes(
                matches, max_preferred_routes
            ),
            "max_weight_kg": remaining,
        },
        "privacy_note": (
            "This brief intentionally excludes driver name, vehicle "
            "registration, internal IDs, and customer-identifying details."
        ),
    }

    brief["generated_text"] = _build_text(brief)
    return brief
