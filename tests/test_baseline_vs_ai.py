'''
Regression test for compare_baseline_vs_ai.

Guards against the cost_per_km -> truck_type/db signature change
that broke the endpoint once already.
'''

from backend.database.connection import SessionLocal
from backend.models.truck import Truck
from backend.services.baseline_vs_ai import compare_baseline_vs_ai


def test_baseline_vs_ai_returns_comparison_for_real_truck():
    db = SessionLocal()
    try:
        truck = db.query(Truck).order_by(Truck.truck_id).first()
        assert truck is not None, "Need at least one seeded truck"

        result = compare_baseline_vs_ai(truck.truck_id, db)

        assert result is not None
        assert result["truck_id"] == truck.truck_id

        assert "experiment" in result
        assert result["experiment"]["database_modified"] is False

        assert "baseline" in result
        assert "ai" in result
        assert "comparison" in result

        # At minimum, one of them should be evaluated when we have
        # the reset/seeded benchmark state.
        assert (
            result["baseline"] is not None
            or result["ai"] is not None
        ), "Neither strategy could be evaluated"

        # If both evaluated, comparison metrics exist
        if result["baseline"] and result["ai"]:
            assert "winner" in result["comparison"]
            assert "profit_difference" in result["comparison"]
            assert "cost_difference" in result["comparison"]

    finally:
        db.close()


def test_baseline_vs_ai_missing_truck():
    db = SessionLocal()
    try:
        result = compare_baseline_vs_ai(999999, db)
        assert result["message"] == "Truck not found"
    finally:
        db.close()
