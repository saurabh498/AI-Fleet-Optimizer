from sqlalchemy.orm import Session

from backend.services.fleet_optimizer import optimize_fleet


def reoptimize_fleet(db: Session):
    """
    Re-run fleet optimization after a fleet state change.
    """

    result = optimize_fleet(db)

    return {
        "message": "Fleet re-optimization completed",
        "optimization": result
    }