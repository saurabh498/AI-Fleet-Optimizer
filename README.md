# AI Fleet Optimizer

**AI-based fleet monitoring, backhaul decision support and logistics optimization system**

AI Fleet Optimizer is a web-based decision-support system designed to help fleet managers reduce empty-truck movement and make better return-load assignment decisions. The system combines real-time location simulation, shipment matching, machine-learning predictions, optimization and a decision engine to recommend what a truck should do after delivery.

> **Project type:** AI/ML + Logistics Optimization + Web Application  
> **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL  
> **Frontend:** React, Vite, Leaflet  
> **ML:** Scikit-learn, XGBoost  
> **Optimization:** OR-Tools  
> **Location:** Simulated GPS with route-based movement

---

## 1. Problem Statement

In real-world logistics, a truck may complete a delivery in one city and then return without cargo. This creates empty kilometres, increases operating cost and reduces vehicle utilization.

The objective of AI Fleet Optimizer is to support the fleet manager by answering:

- Where is each truck currently located?
- Is the truck loaded, empty, assigned, waiting or in transit?
- Are suitable return shipments available near the truck?
- Which shipment is compatible with the truck?
- How profitable and route-efficient is the opportunity?
- What is the predicted demand at the truck's location?
- How long might the truck need to wait?
- Should the system recommend **ASSIGN NOW**, **WAIT**, **REPOSITION** or **RETURN EMPTY**?

The system is a **decision-support and optimization system**. It does not autonomously control real trucks.

---

## 2. Objectives

1. Track truck locations and operational status.
2. Manage trucks, shipments and assignments.
3. Detect delivery completion using simulated GPS movement.
4. Identify feasible return/backhaul shipments.
5. Score shipment opportunities using distance, revenue, utilization, profitability and route efficiency.
6. Predict shipment demand using machine learning.
7. Predict waiting time for future load availability.
8. Optimize truck-to-shipment assignments under operational constraints.
9. Generate an explainable operational recommendation.
10. Compare the AI-based strategy with a simple nearest-compatible-shipment baseline.
11. Provide fleet monitoring and analytics through a React dashboard.

---

## 3. System Architecture

```text
                    ┌──────────────────────────┐
                    │       React Frontend     │
                    │ Dashboard / Fleet /      │
                    │ Shipments / AI /         │
                    │ Analytics                │
                    └────────────┬─────────────┘
                                 │ HTTP / REST
                                 ▼
                    ┌──────────────────────────┐
                    │      FastAPI Backend      │
                    │ REST APIs + Validation    │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
     ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐
     │   PostgreSQL   │ │   AI / ML      │ │ Optimization    │
     │ Trucks         │ │ Demand         │ │ OR-Tools        │
     │ Shipments      │ │ Waiting Time   │ │ Assignment      │
     │ Locations      │ │ Predictions    │ │ Constraints     │
     │ Assignments    │ └───────┬────────┘ └────────┬────────┘
     └────────────────┘         │                   │
                                └────────┬──────────┘
                                         ▼
                              ┌─────────────────────┐
                              │   Decision Engine   │
                              │ ASSIGN / WAIT /     │
                              │ REPOSITION /       │
                              │ RETURN EMPTY       │
                              └─────────────────────┘
```

---

## 4. Main Workflow

```text
Truck Registered
      │
      ▼
Truck Receives Shipment
      │
      ▼
Travel + GPS Location Updates
      │
      ▼
Delivery Completed
      │
      ▼
Truck Becomes Available for Re-evaluation
      │
      ▼
Find Feasible Backhaul Shipments
      │
      ├── Suitable Load Found ──► Score + Optimize ──► Assign
      │
      └── No Suitable Load ─────► Predict Demand + Wait
                                      │
                                      ├── WAIT
                                      ├── REPOSITION
                                      └── RETURN EMPTY
```

---

## 5. Core Features

### Fleet Management
- Create and view trucks.
- Track capacity, current load, city, destination and status.
- Maintain truck location history.

### Shipment Management
- Create and view shipments.
- Track pickup and destination.
- Store weight, volume, cargo type, revenue and time windows.
- Track shipment lifecycle from available to delivered.

### GPS Simulation
- Simulates route-based truck movement.
- Sends periodic latitude/longitude updates to the backend.
- Supports multiple trucks with active assignments.
- Detects arrival at the destination.
- Automatically triggers assignment completion and fleet re-optimization.

### Backhaul Matching
The matching layer checks:
- Truck capacity.
- Shipment availability.
- Pickup distance.
- Route distance.
- Estimated operating cost.
- Estimated profit.
- Capacity utilization.
- Route efficiency.
- Revenue per kilometre.

### AI Decision Support
The decision layer combines operational matching with ML context and produces recommendations such as:
- `ASSIGN_NOW`
- `REVIEW`
- `WAIT`
- `REPOSITION`
- `RETURN_EMPTY`

### Fleet Optimization
The optimization engine uses OR-Tools to assign trucks to shipments while respecting constraints such as:
- One shipment per truck assignment.
- One truck per shipment assignment.
- Truck capacity.
- Availability.
- Assignment conflicts.
- Pickup time feasibility.
- Delivery deadlines.
- Route feasibility.

---

## 6. Machine Learning

### Demand Prediction

The project uses historical/synthetic shipment data to predict future load demand.

- Dataset: **5,000 synthetic historical shipment records**
- Coverage: **14 cities**
- Main model: **XGBoost**
- Model version: `xgboost-v1`
- Saved model: `ml/models/xgboost_demand_model.joblib`

Evaluation:

| Metric | Result |
|---|---:|
| MAE | 2.4102 |
| RMSE | 2.9669 |
| MAPE | 15.47% |

### Waiting-Time Prediction

Waiting time is predicted using regression.

- Main model: **Linear Regression**
- Model version: `baseline-waiting-v1`
- Saved model: `ml/models/baseline_waiting_time_model.joblib`

Evaluation:

| Metric | Result |
|---|---:|
| MAE | 0.8248 hours |
| RMSE | 0.9462 hours |

MAE and RMSE are treated as the primary waiting-time evaluation metrics because the target contains relatively small waiting-time values, which can disproportionately inflate MAPE.

---

## 7. Matching and Decision Logic

The system does not select a shipment using distance alone.

Candidate shipments are evaluated using factors including:

- Pickup distance
- Revenue
- Capacity utilization
- Estimated net revenue/profit
- Revenue per kilometre
- Route efficiency

A higher match score represents a stronger operational opportunity.

The decision layer then combines the matching result with:
- Predicted demand
- Predicted waiting time
- Route efficiency
- Estimated profit
- ML adjustment

This produces an operational recommendation that can be inspected by the fleet manager.

---

## 8. Baseline vs AI Evaluation

The project includes a separate evaluation layer to compare the AI strategy with a simple baseline.

### Baseline

The baseline strategy:
1. Finds the truck.
2. Gets its latest location.
3. Finds available shipments.
4. Applies basic feasibility constraints.
5. Selects the nearest feasible shipment.

The baseline intentionally does **not** use:
- ML
- optimization
- revenue scoring
- profit scoring
- route-efficiency scoring
- recommendation scoring

### Controlled Experiment

The baseline and AI strategies use the same:
- Truck state
- Available shipment pool

The comparison reports:
- Selected load
- Pickup distance
- Delivery distance
- Total distance
- Estimated cost
- Estimated profit
- Capacity utilization
- Difference between strategies

The database is not modified by the comparison endpoint.

Results are interpreted as **controlled scenario comparisons**, not as proof of universal fleet-wide improvement.

---

## 9. Database

PostgreSQL is used as the primary relational database.

Core entities include:

- `trucks`
- `shipments`
- `truck_locations`
- `assignments`
- `assignment_history`
- `historical_shipments`
- `predictions`

A newly created truck with valid coordinates automatically receives an initial `TruckLocation` record. This ensures location-dependent services can immediately use the truck's latest location.

---

## 10. Backend Structure

```text
backend/
├── main.py
├── api/
│   ├── assignments.py
│   ├── backhaul.py
│   ├── demand_prediction.py
│   ├── shipments.py
│   ├── trucks.py
│   ├── truck_locations.py
│   └── waiting_time_prediction.py
├── database/
│   ├── base.py
│   └── connection.py
├── models/
│   ├── assignment.py
│   ├── assignment_history.py
│   ├── historical_shipment.py
│   ├── prediction.py
│   ├── shipment.py
│   ├── truck.py
│   └── truck_location.py
└── services/
    ├── arrival_detection.py
    ├── assignment_decision.py
    ├── automatic_assignment.py
    ├── backhaul_matching.py
    ├── baseline_matching.py
    ├── best_backhaul.py
    ├── demand_prediction.py
    ├── fleet_assignment_executor.py
    ├── fleet_constraints.py
    ├── fleet_optimizer.py
    ├── ml_decision_context.py
    ├── ortools_optimizer.py
    ├── reoptimization.py
    ├── route_optimizer.py
    └── waiting_time_prediction.py
```

---

## 11. Important API Endpoints

### Trucks

```text
GET  /trucks/
POST /trucks/
```

### Shipments

```text
GET  /shipments/
POST /shipments/
GET  /shipments/{load_id}
```

### Truck Locations

```text
POST /locations/
GET  /locations/
GET  /locations/truck/{truck_id}
GET  /locations/truck/{truck_id}/latest
```

### Assignments

```text
POST /assignments/truck/{truck_id}/load/{load_id}
GET  /assignments/
GET  /assignments/{assignment_id}
GET  /assignments/{assignment_id}/details
GET  /assignments/{assignment_id}/history
PUT  /assignments/{assignment_id}/start
PUT  /assignments/{assignment_id}/complete
GET  /assignments/{assignment_id}/arrival
```

### Backhaul and Evaluation

```text
GET /backhaul/match/{truck_id}
GET /backhaul/decision/{truck_id}
GET /backhaul/baseline-vs-ai/{truck_id}
```

Interactive API documentation is available through FastAPI Swagger UI.

---

## 12. Frontend

The React frontend provides the following operational screens:

### Dashboard
- Fleet KPIs
- Shipment overview
- AI recommendations
- Live fleet map
- Fleet status

### Fleet
- Truck list
- Capacity and current load
- Location
- Destination
- Operational status

### Shipments
- Shipment inventory
- Pickup/destination
- Weight
- Cargo type
- Revenue
- Shipment status

### AI Intelligence
- Per-truck recommendation
- Selected load
- Match score
- Route efficiency
- Estimated profit
- Predicted demand
- Predicted waiting time
- ML model information

### Analytics
- Baseline vs AI controlled comparison
- Assignment performance
- Profit
- Distance
- Operating cost
- Recommendation distribution
- Fleet-level operational KPIs

---

## 13. GPS Simulator

The simulator is located at:

```text
simulator/gps_simulator.py
```

Run it from the simulator directory:

```powershell
cd simulator
python gps_simulator.py
```

The simulator discovers trucks currently in transit, follows their active assignment route and posts GPS updates to the backend.

When a truck reaches its destination, the backend can:
1. Detect arrival.
2. Complete the assignment.
3. Mark the shipment delivered.
4. Update the truck state.
5. Trigger fleet re-optimization.
6. Generate the next assignment when a feasible opportunity exists.

---

## 14. End-to-End Demonstration

A controlled demonstration was successfully validated using **Truck #3**.

### Completed lifecycle

```text
Truck #3
   │
   ▼
Load #21: Mumbai → Pune
   │
   ▼
GPS route simulation
   │
   ▼
Automatic arrival detection
   │
   ▼
Assignment #20 completed
   │
   ▼
Load #21 delivered
   │
   ▼
Fleet re-optimization
   │
   ▼
Load #22: Pune → Hyderabad
   │
   ▼
Assignment #21 created and assigned
```

Validated results:

- Assignment #20: `completed`
- Shipment #21: `delivered`
- Assignment #21: `assigned`
- Load #22: Pune → Hyderabad
- Assignment #21 match score: **210**
- Assignment #21 estimated profit: **₹39,356.25**
- Assignment #21 recommendation: **Highly Recommended**

This demonstrates the project's central operational lifecycle: **delivery → location/state update → re-evaluation → return/backhaul assignment**.

---

## 15. Testing

### Backend

```text
pytest
7 passed
7 warnings
```

The warnings are non-blocking deprecation warnings from existing datetime/OR-Tools dependencies.

### Frontend

Lint result:

```text
0 errors
2 warnings
```

The two warnings are React `set-state-in-effect` lint warnings in the Trucks and Shipments data-loading effects.

Build result:

```text
136 modules transformed
Vite production build: PASS
```

The production bundle was successfully generated in `frontend/dist`.

---

## 16. Current Project Status

The implementation has progressed through the planned development phases:

- Phase 0 — Specification: **Complete**
- Phase 1 — Project Setup: **Complete**
- Phase 2 — Core Data: **Complete**
- Phase 3 — GPS Simulator & Real-Time Tracking: **Complete**
- Phase 4 — Basic Matching: **Complete**
- Phase 5 — Optimization: **Complete**
- Phase 6 — Machine Learning: **Complete**
- Phase 7 — Decision Engine: **Complete**
- Phase 8 — React Dashboard: **Complete**
- Phase 9 — Analytics & Baseline Comparison: **Complete**
- Phase 10 — Testing, Documentation & Demo: **In progress**

---

## 17. Limitations

This is a college/research prototype and currently uses simulated logistics data and simulated GPS movement.

Current limitations include:

- Historical shipment data is synthetic.
- GPS data is simulated rather than connected to a production telematics provider.
- Route and travel estimates are intended for prototype evaluation.
- ML predictions depend on the quality and distribution of the training data.
- Production deployment, authentication infrastructure and external logistics integrations would require additional hardening.

---

## 18. Future Scope

Potential future extensions include:

- Live GPS/telematics integration.
- Larger real-world shipment datasets.
- More advanced demand forecasting.
- Real-time traffic and route APIs.
- Driver and vehicle constraints.
- Fuel-price-aware cost modelling.
- Multi-depot and multi-stop optimization.
- Cloud deployment.
- Role-based authentication and authorization.
- Model monitoring and automated retraining.
- Advanced what-if simulation for fleet managers.

---

## 19. Local Setup

### Backend

From the project root:

```powershell
.envScriptsActivate.ps1
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173/
```

### Tests

Backend:

```powershell
.envScriptspython.exe -m pytest -q
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

---

## 20. Project Repository

**GitHub:** https://github.com/saurabh498/AI-Fleet-Optimizer

**Development branch:** `ui/advanced-control-center`

The development branch contains the current control-center UI and finalized project implementation. Merge to `main` only after final project review.

---

## 21. Summary

AI Fleet Optimizer combines:

**Fleet Tracking + Shipment Matching + Machine Learning + Optimization + Decision Support**

to help fleet managers evaluate what a truck should do after completing a delivery.

The system's key demonstration is the ability to simulate a truck's journey, detect delivery completion, update operational state and automatically re-evaluate the fleet for the next suitable shipment.

