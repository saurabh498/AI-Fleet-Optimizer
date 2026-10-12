'''
Driver-hours accumulation.

When a trip completes, compute the elapsed driving time from the
AssignmentHistory record and add it to the driver's counters.

If accumulated time crosses a configured threshold, set rest_required.
Rules come from config/driver_rules.yaml and are NOT legally verified.
'''

from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.assignment import Assignment
from backend.models.assignment_history import AssignmentHistory
from backend.models.driver import Driver
from backend.models.truck import Truck
from backend.services.driver_feasibility import get_rule, is_rules_verified


def get_driver_for_truck(truck_id: int, db: Session) -> Driver | None:
    '''Return the driver currently bound to this truck, or None.'''
    return db.query(Driver).filter(
        Driver.assigned_truck_id == truck_id
    ).first()


def apply_completion_to_driver(
    assignment: Assignment,
    db: Session,
) -> dict | None:
    '''
    Called after an assignment's status becomes 'completed'.
    Looks up the truck's driver and adds the elapsed trip time.

    Returns a summary dict, or None if no driver / no history.
    '''
    truck_id = assignment.truck_id

    driver = get_driver_for_truck(truck_id, db)
    if driver is None:
        return None

    # Find the moment this assignment became 'in_transit'
    started = (
        db.query(AssignmentHistory)
        .filter(
            AssignmentHistory.assignment_id == assignment.assignment_id,
            AssignmentHistory.status == "in_transit",
        )
        .order_by(AssignmentHistory.changed_at.desc())
        .first()
    )

    if started is None:
        return {
            "driver_id": driver.driver_id,
            "elapsed_minutes": 0,
            "reason": "No in_transit history entry; skipped",
        }

    now = datetime.utcnow()
    elapsed_minutes = int(
        (now - started.changed_at).total_seconds() // 60
    )
    if elapsed_minutes < 0:
        elapsed_minutes = 0

    driver.accumulated_driving_minutes = (
        (driver.accumulated_driving_minutes or 0) + elapsed_minutes
    )
    driver.accumulated_since_last_rest_minutes = (
        (driver.accumulated_since_last_rest_minutes or 0) + elapsed_minutes
    )

    # Threshold checks
    max_cont = get_rule("max_continuous_driving_minutes")
    max_daily = get_rule("max_daily_driving_minutes")

    triggered = []
    if max_cont and driver.accumulated_since_last_rest_minutes >= max_cont:
        driver.rest_required = True
        triggered.append("max_continuous_driving_minutes")
    if max_daily and driver.accumulated_driving_minutes >= max_daily:
        driver.rest_required = True
        triggered.append("max_daily_driving_minutes")

    db.commit()

    return {
        "driver_id": driver.driver_id,
        "elapsed_minutes": elapsed_minutes,
        "accumulated_driving_minutes": driver.accumulated_driving_minutes,
        "accumulated_since_last_rest_minutes": (
            driver.accumulated_since_last_rest_minutes
        ),
        "rest_required": driver.rest_required,
        "thresholds_triggered": triggered,
        "rules_verified_against_law": is_rules_verified(),
    }


def apply_rest_taken(driver: Driver, db: Session) -> dict:
    '''Reset continuous-driving counter and clear rest_required.'''
    driver.accumulated_since_last_rest_minutes = 0
    driver.last_rest_time = datetime.utcnow()
    driver.rest_required = False
    db.commit()
    return {
        "driver_id": driver.driver_id,
        "last_rest_time": driver.last_rest_time.isoformat(),
        "accumulated_since_last_rest_minutes": 0,
        "rest_required": False,
    }
