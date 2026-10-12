'''Verify driver feasibility integration into the decision engine.'''

from datetime import datetime, timedelta
from unittest.mock import patch

from backend.database.connection import SessionLocal
from backend.models.driver import Driver
from backend.models.truck import Truck
from backend.services.assignment_decision import (
    generate_assignment_decision,
)


def _make_truck(db, status='available'):
    t = Truck(
        truck_type='HCV',
        capacity=15000,
        current_load=0,
        cost_per_km=35.0,
        status=status,
        current_city='Mumbai',
        current_latitude=19.0760,
        current_longitude=72.8777,
    )
    db.add(t)
    db.flush()
    return t


def _make_driver(db, truck_id, **overrides):
    defaults = dict(
        display_name='Decision Test Driver',
        availability_status='available',
        assigned_truck_id=truck_id,
        accumulated_driving_minutes=60,
        accumulated_since_last_rest_minutes=60,
    )
    defaults.update(overrides)
    d = Driver(**defaults)
    db.add(d)
    db.flush()
    return d


def _mock_best_match():
    return {
        'load_id': 999,
        'match_score': 200,
        'decision_score': 200,
        'route_efficiency_score': 90,
        'estimated_route_profit': 20000,
        'distance_to_pickup_km': 50,
        # 100 km at 45 km/h = ~133 min
        # Driver accumulated_since_last_rest = 60 min
        # Total = 193 <= max_continuous (240) -> feasible
        'route': {'total_distance_km': 100},
    }


def _mock_ml_context():
    return {
        'truck_id': 1,
        'available': True,
        'city': 'Mumbai',
        'predicted_demand': 35.0,
        'predicted_waiting_time': 1.5,
        'demand_model': 'XGBoost Regressor',
        'demand_model_version': 'xgboost-v1',
        'waiting_model': 'Linear Regression',
        'waiting_model_version': 'baseline-waiting-v1',
    }


# -------------------------------------------------
# No driver bound - unchanged behavior
# -------------------------------------------------

def test_no_driver_keeps_assign_now():
    db = SessionLocal()
    t = _make_truck(db)
    db.commit()
    try:
        with patch(
            'backend.services.assignment_decision.select_best_backhaul',
            return_value={'best_match': _mock_best_match()},
        ), patch(
            'backend.services.assignment_decision.build_ml_decision_context',
            return_value=_mock_ml_context(),
        ):
            r = generate_assignment_decision(t.truck_id, db)
        assert r['decision'] == 'ASSIGN_NOW'
        assert r['driver_feasibility'] is None
    finally:
        db.query(Truck).filter(Truck.truck_id == t.truck_id).delete()
        db.commit()
        db.close()


# -------------------------------------------------
# Driver bound + infeasible -> downgraded
# -------------------------------------------------

def test_unavailable_driver_downgrades_assign_now():
    db = SessionLocal()
    t = _make_truck(db)
    d = _make_driver(db, t.truck_id, availability_status='off_duty')
    db.commit()
    try:
        with patch(
            'backend.services.assignment_decision.select_best_backhaul',
            return_value={'best_match': _mock_best_match()},
        ), patch(
            'backend.services.assignment_decision.build_ml_decision_context',
            return_value=_mock_ml_context(),
        ):
            r = generate_assignment_decision(t.truck_id, db)
        assert r['decision'] == 'REVIEW'
        assert 'driver' in r['reason'].lower()
        assert r['driver_feasibility']['feasible'] is False
    finally:
        db.query(Driver).filter(Driver.driver_id == d.driver_id).delete()
        db.query(Truck).filter(Truck.truck_id == t.truck_id).delete()
        db.commit()
        db.close()


def test_rest_required_driver_downgrades():
    db = SessionLocal()
    t = _make_truck(db)
    d = _make_driver(db, t.truck_id, rest_required=True)
    db.commit()
    try:
        with patch(
            'backend.services.assignment_decision.select_best_backhaul',
            return_value={'best_match': _mock_best_match()},
        ), patch(
            'backend.services.assignment_decision.build_ml_decision_context',
            return_value=_mock_ml_context(),
        ):
            r = generate_assignment_decision(t.truck_id, db)
        assert r['decision'] == 'REVIEW'
        assert 'rest' in r['reason'].lower()
    finally:
        db.query(Driver).filter(Driver.driver_id == d.driver_id).delete()
        db.query(Truck).filter(Truck.truck_id == t.truck_id).delete()
        db.commit()
        db.close()


# -------------------------------------------------
# Driver bound + feasible -> still has REVIEW flag (unverified rules)
# -------------------------------------------------

def test_feasible_driver_still_flags_review():
    db = SessionLocal()
    t = _make_truck(db)
    d = _make_driver(db, t.truck_id)
    db.commit()
    try:
        with patch(
            'backend.services.assignment_decision.select_best_backhaul',
            return_value={'best_match': _mock_best_match()},
        ), patch(
            'backend.services.assignment_decision.build_ml_decision_context',
            return_value=_mock_ml_context(),
        ):
            r = generate_assignment_decision(t.truck_id, db)
        assert r['decision'] == 'ASSIGN_NOW'
        df = r['driver_feasibility']
        assert df is not None
        assert df['feasible'] is True
        # Because rules are unverified, review is still required
        assert df['requires_review'] is True
        assert df['rules_verified_against_law'] is False
    finally:
        db.query(Driver).filter(Driver.driver_id == d.driver_id).delete()
        db.query(Truck).filter(Truck.truck_id == t.truck_id).delete()
        db.commit()
        db.close()


# -------------------------------------------------
# No-match branch also returns driver_feasibility
# -------------------------------------------------

def test_no_match_includes_driver_feasibility():
    db = SessionLocal()
    t = _make_truck(db)
    d = _make_driver(db, t.truck_id)
    db.commit()
    try:
        with patch(
            'backend.services.assignment_decision.select_best_backhaul',
            return_value={
                'best_match': None,
                'waiting_recommendation': {
                    'recommended_waiting_time_hours': 3
                },
            },
        ), patch(
            'backend.services.assignment_decision.build_ml_decision_context',
            return_value={
                **_mock_ml_context(),
                'predicted_demand': 8.0,
                'predicted_waiting_time': 6.0,
            },
        ):
            r = generate_assignment_decision(t.truck_id, db)
        assert 'driver_feasibility' in r
        assert r['driver_feasibility'] is not None
        assert r['driver_feasibility']['driver_id'] == d.driver_id
    finally:
        db.query(Driver).filter(Driver.driver_id == d.driver_id).delete()
        db.query(Truck).filter(Truck.truck_id == t.truck_id).delete()
        db.commit()
        db.close()
