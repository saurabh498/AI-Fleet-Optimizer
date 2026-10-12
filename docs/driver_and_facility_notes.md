# Driver & Facility — Design Notes

This document explains the *reasoning* behind the driver and rest-facility
features, so a reviewer can see why the design is what it is, not just what
it does.

---

## Drivers

### Why a separate Driver entity rather than a User flag

- A user is an authentication identity. A driver is an operational resource.
- Not every driver will log into the system (some will be entered by a
  dispatcher). Not every user is a driver (managers, admins).
- The two are linked optionally via Driver.user_id when auth is desired.
- A truck can exist without a driver; a driver can exist without a truck.

### Location source of truth

The project rule is: **latest TruckLocation is authoritative for truck
position**. For a driver:

- When the driver is bound to a truck (ssigned_truck_id is set), the
  truck's position is authoritative. Driver current_latitude /
  current_longitude are not consulted.
- When the driver is unbound, their own coordinates are a fallback.

The decision engine only ever uses the truck's position.

### Assignment feasibility is a pure function

check_driver_feasibility(driver, truck, estimated_trip_minutes) has no
database session and no side effects. It returns:

    { feasible, reason, requires_review, missing_data }

This makes it trivially testable and lets the caller decide what to do.

### Triggering the "rest required" flag

The flag is set in two ways:

1. **Explicitly** by an API call (POST /drivers/{id}/rest-taken clears it,
   but a dispatcher can set it via PUT).
2. **Automatically** by pply_completion_to_driver, which runs when an
   assignment is completed and adds elapsed trip minutes to the counters.
   If either the continuous or daily threshold is crossed, est_required
   is set.

### Feasibility does not block; it downgrades

A driver who is off-duty or needs rest does **not** cause the shipment to
be rejected. ASSIGN_NOW is downgraded to REVIEW, with a reason string
naming the specific blocker. This preserves the existing API contract while
surfacing the operational concern.

### Rules are not verified

See docs/assumptions.md §5. The system's honesty flag
ules_verified_against_law propagates all the way to the API response.
A teacher, reviewer, or auditor can see at a glance that the values are
placeholders pending legal review.

---

## Rest facilities

### Only verified facilities are used

suggest_rest_facility filters to erification_status == 'verified'.
Rows in pending state are stored but never suggested.

This means: no unverified data reaches the decision engine, even if it's
already in the DB.

### Distance uses the same routing service as shipments

The suggestion function calls get_route(...) from the existing routing
service. This means:

- OSRM road distance when available, cached in Postgres
- Haversine fallback when OSRM is down, explicitly marked in the response
  as distance_source: "haversine"

No separate distance logic. The API response marks which mode was used so
a reviewer never confuses a straight-line estimate with a road distance.

### A facility is a suggestion, not a decision

The suggestion does not change decision. It appears as
est_facility_suggestion — an object with a recommended action *label*
(WAIT_AT_REST_FACILITY or REPOSITION_TO_REST_FACILITY) and the
facility details.

The fleet manager is the final decision-maker. The system proposes; it
does not dispatch.

### Missing data is surfaced, never assumed

If:
- The driver needs rest but the truck has no coordinates, or
- No verified facility exists in the search bbox, or
- The routing service failed for every candidate,

…the response still contains the suggestion object, but with
acility: null and a equires_review: true reason explaining what
was missing.

**No facility is ever recommended on invented or unverified data.**

### Why 75% as the "approaching limit" threshold

A driver who is 75% of the way to the continuous-driving limit is likely
to hit it during the next trip. Flagging them at that point gives the
manager time to plan a rest stop before the limit is crossed.

The 0.75 ratio is a heuristic, not a legal rule. It lives in
est_facility_recommendation.py as APPROACHING_RATIO and can be tuned
without a schema change.

### What is *not* modelled

- **Live facility availability** (parking spaces, dormitory beds).
  No public source provides this. The system never claims a facility is
  currently available.
- **Quality ratings, amenities verification.** The vailable_amenities
  field is free-form and only populated when the source documents it.
- **Payment methods, fuel availability at the facility.** Out of scope.

If any of these become available as APIs later, they belong in the same
suggestion object as additional fields.

---

## Combined flow — end-to-end

1. Driver completes a trip → pply_completion_to_driver runs.
2. Driver's accumulated minutes increase.
3. If the continuous or daily threshold is crossed, est_required = True.
4. Next decision request: uild_driver_decision_context marks the driver
   infeasible.
5. generate_assignment_decision downgrades ASSIGN_NOW → REVIEW.
6. If the decision was WAIT or REPOSITION, suggest_rest_facility runs.
7. A verified facility within the bbox is chosen by OSRM road distance.
8. The response carries both driver_feasibility and
   est_facility_suggestion.
9. The manager sees the annotation and decides.

No step auto-executes. Every response is explainable.
