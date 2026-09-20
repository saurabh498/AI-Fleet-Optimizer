# 🚛 AI Fleet Optimizer

**AI-powered decision support for freight backhaul optimization.**

Reduces empty kilometres, increases profit, and cuts CO₂ by matching trucks
with return loads using real road distances, machine learning, and
multi-objective optimization.

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/tests-72%20passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Final-year college project** — runs entirely on localhost.
> See [Quick Start](#quick-start) below.

---

## The Problem

In Indian road freight, **20–40% of truck kilometres are empty**. A truck
delivers Mumbai → Delhi and returns empty because the dispatcher couldn't
find a suitable return shipment in time. This wastes fuel, money, driver
hours, and emits unnecessary CO₂.

Existing tools show loads on a map. They don't decide **whether to assign
now, wait, reposition, or return empty**. This system does.

---

## What It Does

Given a truck that just completed a delivery, the system:

1. **Finds every feasible backhaul shipment** — respecting capacity, weight, cargo type, and time windows
2. **Computes real road distance** via OSRM (not straight-line estimates)
3. **Predicts demand and waiting time** in the truck's city and each candidate destination
4. **Scores each candidate** on revenue, cost, route efficiency, CO₂, and ML predictions
5. **Explains every recommendation** with SHAP feature contributions
6. **Recommends an action**: `ASSIGN_NOW` · `REVIEW` · `WAIT` · `REPOSITION` · `RETURN_EMPTY`

Every API response includes a cost breakdown, CO₂ estimate, and a
human-readable SHAP summary. A built-in **server-side GPS simulator**
button lets you watch trucks move on the live map without needing a
terminal.

---

## Screenshots

### Login
![Login screen](docs/screenshots/01-login.png)

### Fleet Dashboard — KPI + Environmental Impact
![Dashboard](docs/screenshots/02-dashboard.png)

### AI Recommendation with SHAP Explainability
![AI Recommendation](docs/screenshots/03-ai-recommendation.png)

### Analytics — Baseline vs AI + Cost Breakdown
![Analytics](docs/screenshots/04-analytics.png)

### Live Fleet Map
![Fleet Map](docs/screenshots/05-fleet-map.png)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  React Dashboard (Leaflet map, KPI cards, decision panel)        │
│  • JWT auth  • Role-based nav  • Token auto-refresh              │
└──────────────────────────┬───────────────────────────────────────┘
                           │  REST / JSON
┌──────────────────────────▼───────────────────────────────────────┐
│  FastAPI Backend                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Trucks /    │  │ Backhaul    │  │ Decision     │  │ Fleet    │ │
│  │ Shipments   │  │ Matching    │  │ Engine + ML  │  │ Optimizer│ │
│  └─────────────┘  └──────┬──────┘  └──────┬───────┘  └────┬─────┘ │
│                          │                 │               │       │
│  ┌───────────────────────▼─────────────────▼───────────────▼─────┐ │
│  │  JWT + RBAC  •  OSRM cache  •  SHAP  •  Cost + CO₂ model      │ │
│  └───────────────────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────────────────┘
                           │
              ┌────────────▼─────────────┐
              │  PostgreSQL 16           │
              │  users · trucks ·        │
              │  shipments · locations · │
              │  routes · predictions    │
              └──────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite 8, Leaflet, React Router 7 |
| Backend | FastAPI, SQLAlchemy 2, Pydantic 2 |
| Database | PostgreSQL 16 |
| ML | XGBoost, scikit-learn, SHAP, pandas |
| Optimization | Google OR-Tools |
| Routing | OSRM (real road distances) |
| Auth | bcrypt + PyJWT (HS256) |
| Testing | pytest, FastAPI TestClient |

---

## Quick Start

**Prerequisites:** Python 3.13, Node 22, PostgreSQL 16.

```powershell
git clone https://github.com/saurabh498/AI-Fleet-Optimizer.git
cd AI-Fleet-Optimizer

# Backend setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

**Configure PostgreSQL** — create a database called `fleet_optimizer`
and set the connection string:

```powershell
# .env file in project root
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fleet_optimizer
```

**Create tables + seed users:**

```powershell
python -c "from backend.database.connection import engine; from backend.database.base import Base; import backend.models; Base.metadata.create_all(bind=engine)"
python -m scripts.seed_users
```

**Seed data + train ML models:**

```powershell
python -m ml.generate_historical_data --full-year
python -m ml.xgboost_demand_model
python -m ml.xgboost_waiting_time_model
```

**Run backend:**

```powershell
uvicorn backend.main:app --reload --port 8000
```

**Frontend (new terminal):**

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and log in with:

| Role | Email | Password |
|---|---|---|
| Admin | `admin@fleetops.in` | `admin123` |
| Manager | `manager@fleetops.in` | `manager123` |
| Driver | `driver@fleetops.in` | `driver123` |

API docs: **http://localhost:8000/docs**

---

## Authentication & Roles

| Role | Read | Write fleet data | Analytics | Location updates |
|---|---|---|---|---|
| **Admin** | ✅ | ✅ | ✅ | ✅ |
| **Manager** | ✅ | ✅ | ✅ | ✅ |
| **Driver** | ✅ | — | — | ✅ |

JWT access tokens (30 min) + refresh tokens (7 days). Axios interceptor
auto-refreshes on 401 without interrupting the user. Passwords hashed
with bcrypt.

The navbar **filters links by role** — drivers don't see the Analytics
tab, and write buttons ("Add Truck", "Edit", "Delete") are hidden for
non-manager roles.

---

## GPS Simulator

Two ways to run it:

**1. Server-side (recommended for demos)** — click **🛰️ Run GPS Simulator**
on the Dashboard. The backend runs the full route simulation in a
background task; the frontend polls for updates and shows live movement
on the Fleet Map. No terminal needed.

**2. Standalone script** — for debugging or CI:

```powershell
# Local backend
$env:SIM_BASE_URL = "http://127.0.0.1:8000"
python -m simulator.gps_simulator
```

Either way, the simulator only moves trucks whose assignments are
`in_transit`. If no truck is in transit, you'll see a friendly
"No trucks are currently in transit" message.

---

## ML Model Performance

Trained on a **122,640-row dataset** generated from real Indian city
economic data (UN Urbanization Prospects, Census of India, MOSPI) and
NHAI-published freight traffic patterns. Fully reproducible via `--seed 42`.

### Demand Prediction

| Model | MAE | RMSE | MAPE |
|---|---:|---:|---:|
| Linear Regression (baseline) | 1.21 | 1.43 | 12.49% |
| Random Forest | 1.02 | 1.28 | 8.36% |
| **XGBoost** ⭐ | **0.89** | **1.12** | **7.01%** |

### Waiting-Time Prediction

| Model | MAE (hours) | RMSE | MAPE |
|---|---:|---:|---:|
| Linear Regression (baseline) | 0.34 | 0.44 | 14.22% |
| XGBoost | 0.28 | 0.35 | 10.54% |
| **Random Forest** ⭐ | **0.28** | **0.35** | 10.56% |

Every prediction is explainable via **SHAP** — the API returns the top-3
features that drove each forecast in plain English.

---

## Baseline vs AI — Fleet Benchmark

Run on **3 trucks**, **50 shipments** across 14 Indian cities with real
OSRM road distances, real fuel/toll/driver/maintenance costs, and IPCC
CO₂ factors.

| Strategy | Distance (km) | Cost (₹) | Profit (₹) | CO₂ (kg) |
|---|---:|---:|---:|---:|
| Nearest-neighbor (naive) | 957 | 34,190 | 19,910 | 733 |
| Greedy profit (revenue only) | 8,629 | 308,163 | **−173,563** | 6,607 |
| OR-Tools rules | 974 | 34,788 | 28,312 | 746 |
| **Full AI system** | **974** | **34,788** | **28,312** | **746** |

### Key Findings

- **Greedy revenue maximization is catastrophic** — losing ₹174k and
  emitting 7× the CO₂ because it ignores route cost entirely.
- **AI beats nearest-neighbor by +42% profit** at nearly identical
  distance (+1.75%).
- **AI matches rule-based scoring** on this sample. With 3 trucks in the
  same city, ML adjustment is constant per truck — rules already capture
  the win. AI adds per-truck ML context, SHAP explainability, and
  CO₂-aware scoring on top.
- **Next test**: larger fleet with trucks in different cities, where ML
  context genuinely diverges.

Reproduce:

```powershell
python -m scripts.reset_benchmark_state
python -m scripts.seed_benchmark_shipments --count 50 --clear --seed 42
python -m scripts.run_benchmark
```

---

## Data Sources

Every input traces to a public source. Full citations:
[`docs/data_sources.md`](docs/data_sources.md).

| Data | Source |
|---|---|
| City population | UN Urbanization Prospects 2018 + Census of India 2011 |
| Industrial index | MOSPI Annual Survey of Industries |
| Hourly freight curve | NHAI toll plaza aggregates |
| Seasonal effects | Monsoon + festival freight patterns |
| Diesel CO₂ factor | IPCC 2006 Guidelines |

---

## Project Structure

```
.
├── backend/
│   ├── api/                 # FastAPI routers (auth, trucks, shipments, ...)
│   ├── database/            # SQLAlchemy engine + session
│   ├── models/              # ORM models (User, Truck, Shipment, ...)
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   │   ├── auth.py          # JWT + bcrypt
│   │   ├── routing.py       # OSRM + cache + haversine fallback
│   │   ├── cost_model.py    # Fuel + driver + toll + maintenance
│   │   ├── emissions.py     # IPCC CO2 model
│   │   ├── backhaul_matching.py
│   │   ├── assignment_decision.py
│   │   └── benchmark.py     # 4-way fleet benchmark
│   └── main.py
├── frontend/                # React 19 + Vite
│   ├── src/context/         # AuthContext
│   ├── src/components/      # ProtectedRoute, Navbar, ConfirmDialog, ...
│   ├── src/hooks/           # useRole
│   └── src/services/        # api.js (axios + interceptor), auth.js
├── ml/
│   ├── generate_historical_data.py
│   ├── explainability.py    # SHAP wrapper
│   ├── xgboost_*.py
│   └── models/              # Trained .joblib artifacts
├── simulator/
│   └── gps_simulator.py     # Standalone simulator script
├── scripts/                 # Benchmark CLI, seeders
├── tests/                   # 72 tests
├── config/cost_model.yaml   # Tunable rates
├── data/india_cities.json   # Real city data
├── docs/data_sources.md
└── reports/                 # Benchmark outputs
```

---

## Testing

```powershell
python -m pytest tests/ -v --ignore=tests/test_duplicate_execution.py
```

**72 tests** covering:

- JWT auth (hashing, tokens, login, refresh, /me)
- RBAC (anonymous blocked, driver, manager, admin — reads + writes)
- OSRM routing (cache, fallback, timing)
- SHAP explainability (output shape, missing-feature errors)
- Cost model (per-class mileage, breakdown integrity, edge cases)
- Emissions (scaling, per-km ratios)
- Decision engine (boundaries, conflicts, priority, E2E)
- Benchmark strategies (direction, conflicts, aggregation)
- CO₂-aware scoring (penalties, reasons)
- Historical data generation (determinism, distributions)
- Baseline vs AI comparison
- Realistic cost + emissions scaling

---

## Design Decisions

**Why OSRM over straight-line?** Real road distances are ~20–30% longer
than haversine. Using the wrong distance distorts every downstream score
(profit, efficiency, CO₂). OSRM results are cached in Postgres so repeat
lookups are instant.

**Why a full cost model?** "Cost = distance × rate" hides where money
goes. A manager needs fuel vs. driver vs. toll vs. maintenance to make
trade-offs. The model lives in `config/cost_model.yaml` — tunable without
code changes.

**Why SHAP?** Black-box recommendations don't build trust. Every decision
comes with the top-3 features that drove it, in plain English.

**Why a deterministic data generator?** Public hourly freight datasets
for India don't exist. Instead of random noise, the generator uses real
city economics + real traffic curves, and is fully reproducible via
`--seed`.

**Why benchmark against 4 strategies?** "Our AI works" is not evidence.
Showing AI vs. naive vs. greedy vs. rules — with real numbers — is.

---

## Current Limitations

- **Synthetic benchmark data.** Real OSRM distances and real cost/CO₂
  models, but the shipment pool is generated. Real telematics would
  strengthen the results.
- **Small fleet.** 3 trucks in the current test set. Larger fleets with
  geographic diversity would surface AI's differentiation more clearly.
- **Public OSRM demo server** used for road distances (rate-limited).
  Self-hosting is a production upgrade.
- **Cost rates are 2024 industry-typical**, not a specific fleet's
  actual P&L. Configurable in `config/cost_model.yaml`.
- **Runs on localhost.** No cloud deployment — this is intentional for a
  college project demonstration.

---

## Roadmap

- [x] OSRM routing with Postgres cache
- [x] SHAP explainability
- [x] Realistic data generator with real inputs
- [x] Full cost + CO₂ model
- [x] 4-way fleet benchmark
- [x] JWT auth + RBAC
- [x] Frontend auth integration
- [x] KPI dashboard with CO₂ + SHAP
- [x] Role-based navbar
- [x] Edit/delete CRUD from UI
- [x] Server-side GPS simulator button
- [ ] WebSocket live truck tracking
- [ ] Multi-depot VRPTW

---

## License

MIT — see [LICENSE](LICENSE).

---

## Author

**Saurabh** — [GitHub](https://github.com/saurabh498)

Final-year college project exploring the intersection of ML,
optimization, and logistics.