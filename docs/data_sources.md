# Data Sources

Every input used by ml/generate_historical_data.py traces to a
public source. This document lists them.

## City economic data (data/india_cities.json)

| Field | Source |
|---|---|
| population_2025 | UN World Urbanization Prospects 2018 (2025 projections), adjusted with Census of India 2011 baseline |
| latitude, longitude | OpenStreetMap |
| industrial_index | MOSPI Annual Survey of Industries, normalized 0.80-1.30 |

## Freight traffic patterns

| Pattern | Source | Range in code |
|---|---|---|
| Hour-of-day curve | NHAI toll plaza hourly traffic data (published aggregates) | HOUR_FACTOR |
| Day-of-week curve | NHAI weekly toll volumes | DOW_FACTOR |
| Seasonal effects | Monsoon (Jun-Sep) + festival season (Oct-Nov) freight volumes | MONTH_FACTOR |
| Waiting time model | Logistic relationship between demand and wait, calibrated to Indian freight forwarder reports | compute_waiting_time() |
| Completion rate | NHAI throughput data by hour-of-day | compute_completion_rate() |

## Reproducibility

All random draws use Python's andom.Random(seed) with seed defaulting
to 42. Given the same seed and the same india_cities.json, the generator
produces byte-identical output.

Regenerate with:

    python -m ml.generate_historical_data --force --seed 42

## Limitations

- Does not model city-to-city freight flow (only city-level aggregates).
- Does not include weather, fuel prices, or strikes.
- Population and industrial index are single snapshots, not time-series.
- Meant for ML training and evaluation, not for real operational planning.
