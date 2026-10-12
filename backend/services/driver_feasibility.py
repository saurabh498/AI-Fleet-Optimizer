'''
Driver feasibility checks.

⚠️  DRIVING-HOUR RULES ARE NOT LEGALLY VERIFIED
The rules in config/driver_rules.yaml are placeholders. The
system flags every passing check as 'requires_review: true'
while 'metadata.verified_against_law' is false.
'''

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml

from backend.models.driver import Driver
from backend.models.truck import Truck


CONFIG_PATH = Path("config/driver_rules.yaml")


@lru_cache(maxsize=1)
def load_rules() -> dict:
    with CONFIG_PATH.open(encoding="utf-8-sig") as f:
        return yaml.safe_load(f)


def get_rule(name: str, default=None):
    return load_rules().get("rules", {}).get(name, default)


def is_rules_verified() -> bool:
    return bool(load_rules().get("metadata", {}).get("verified_against_law"))


# -------------------------------------------------
# Feasibility check (pure, no side effects)
# -------------------------------------------------

def check_driver_feasibility(
    driver: Optional[Driver],
    truck: Truck,
    estimated_trip_minutes: int,
) -> dict:
    '''
    Return:
        {
            feasible: bool,
            reason: str,
            requires_review: bool,
            missing_data: list[str],
        }
    without mutating state. The caller decides what to do.
    '''

    # No driver linked at all
    if driver is None:
        return {
            "feasible": False,
            "reason": "No driver assigned to this truck",
            "requires_review": True,
            "missing_data": ["driver"],
        }

    # Status gate
    if driver.availability_status not in ("available", "on_duty"):
        return {
            "feasible": False,
            "reason": (
                f"Driver availability_status is "
                f"'{driver.availability_status}'"
            ),
            "requires_review": False,
            "missing_data": [],
        }

    # Truck conflict
    if (
        driver.assigned_truck_id is not None
        and driver.assigned_truck_id != truck.truck_id
    ):
        return {
            "feasible": False,
            "reason": (
                f"Driver already assigned to truck "
                f"{driver.assigned_truck_id}"
            ),
            "requires_review": False,
            "missing_data": [],
        }

    # Rest flag - hard block
    if driver.rest_required:
        return {
            "feasible": False,
            "reason": "Driver rest is required before the next trip",
            "requires_review": False,
            "missing_data": [],
        }

    # Data completeness
    missing = []
    if driver.accumulated_driving_minutes is None:
        missing.append("accumulated_driving_minutes")
    if driver.accumulated_since_last_rest_minutes is None:
        missing.append("accumulated_since_last_rest_minutes")

    if missing:
        return {
            "feasible": False,
            "reason": (
                "Insufficient driver data for a compliance check; "
                "manual review required"
            ),
            "requires_review": True,
            "missing_data": missing,
        }

    # Continuous-driving rule
    max_cont = get_rule("max_continuous_driving_minutes")
    if max_cont is not None:
        projected = (
            driver.accumulated_since_last_rest_minutes
            + estimated_trip_minutes
        )
        if projected > max_cont:
            return {
                "feasible": False,
                "reason": (
                    f"Trip would exceed continuous-driving limit "
                    f"({projected} > {max_cont} min)"
                ),
                "requires_review": True,
                "missing_data": [],
            }

    # Daily rule
    max_daily = get_rule("max_daily_driving_minutes")
    if max_daily is not None:
        projected = (
            driver.accumulated_driving_minutes
            + estimated_trip_minutes
        )
        if projected > max_daily:
            return {
                "feasible": False,
                "reason": (
                    f"Trip would exceed daily-driving limit "
                    f"({projected} > {max_daily} min)"
                ),
                "requires_review": True,
                "missing_data": [],
            }

    # Passed all configured rules
    return {
        "feasible": True,
        "reason": "All configured driver checks passed",
        # Because rules are not legally verified, we still ask
        # a human to review before dispatching.
        "requires_review": not is_rules_verified(),
        "missing_data": [],
    }
