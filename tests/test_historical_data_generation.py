import random
from datetime import date

from ml.generate_historical_data import (
    build_record,
    compute_demand,
    compute_waiting_time,
    generate_compact,
    load_cities,
    HOUR_FACTOR,
    DOW_FACTOR,
)


def test_cities_file_has_14_cities():
    cities = load_cities()
    assert len(cities) == 14
    assert all("industrial_index" in c for c in cities)
    assert all("population_2025" in c for c in cities)


def test_generator_is_deterministic():
    rng_a = random.Random(42)
    rng_b = random.Random(42)
    cities = load_cities()

    records_a = generate_compact(rng_a, 200, cities)
    records_b = generate_compact(rng_b, 200, cities)

    for a, b in zip(records_a, records_b):
        assert a.city == b.city
        assert a.hour == b.hour
        assert a.average_demand == b.average_demand


def test_different_seed_gives_different_output():
    cities = load_cities()

    rec_a = generate_compact(random.Random(1), 100, cities)
    rec_b = generate_compact(random.Random(2), 100, cities)

    pairs = list(zip(rec_a, rec_b))
    assert any(a.average_demand != b.average_demand for a, b in pairs)


def test_weekday_demand_higher_than_sunday():
    mumbai = [c for c in load_cities() if c["name"] == "Mumbai"][0]

    monday = compute_demand(mumbai, date(2024, 3, 4), 9, 0.0)   # Monday
    sunday = compute_demand(mumbai, date(2024, 3, 3), 9, 0.0)   # Sunday

    assert monday > sunday
    assert monday / sunday > 1.5


def test_peak_hours_higher_than_night():
    mumbai = [c for c in load_cities() if c["name"] == "Mumbai"][0]

    peak = compute_demand(mumbai, date(2024, 3, 4), 8, 0.0)
    night = compute_demand(mumbai, date(2024, 3, 4), 3, 0.0)

    assert peak > night
    assert peak / night > 3.0


def test_waiting_time_inversely_correlated_with_demand():
    low_wait = compute_waiting_time(demand=30.0, noise=0.0)
    high_wait = compute_waiting_time(demand=2.0, noise=0.0)

    assert low_wait < high_wait


def test_record_has_no_negative_values():
    mumbai = [c for c in load_cities() if c["name"] == "Mumbai"][0]
    rng = random.Random(7)

    for _ in range(50):
        rec = build_record(mumbai, date(2024, 6, 15), 12, rng)
        assert rec.average_demand > 0
        assert rec.average_waiting_time > 0
        assert rec.available_loads >= 1
        assert rec.completed_loads >= 0
        assert rec.completed_loads <= rec.available_loads
