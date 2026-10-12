# Presentation Summary — Change Report

For internal review and viva use. Every item is labelled.

**Legend:**
- ✅ **Implemented** — merged on eat/driver-and-rest-facilities, tested
- 🟡 **Proposed** — designed, not yet built
- 🔵 **Future scope** — long-term, out of current scope

---

## 1. Driver management

| Item | Status | Notes |
|---|---|---|
| Driver entity with nullable FK to User and Truck | ✅ | |
| Availability status field | ✅ | available, on_duty, resting, off_duty, inactive |
| CRUD API with RBAC | ✅ | writes require manager or admin |
| Driver feasibility service (pure function) | ✅ | no side effects, fully testable |
| Configurable driving-hour rules | ✅ | config/driver_rules.yaml |
| Rules marked as *not* legally verified | ✅ | erified_against_law: false |
| Automatic hours accumulation on trip completion | ✅ | pply_completion_to_driver |
| Auto-flag est_required on threshold crossing | ✅ | |
| /rest-taken endpoint to reset counters | ✅ | |
| Frontend Drivers page (list, create, assign) | 🟡 | Backend ready; UI not started |
| Multi-driver-per-truck rostering | 🔵 | Out of scope |

## 2. Rest facilities

| Item | Status | Notes |
|---|---|---|
| RestFacility entity with mandatory provenance | ✅ | source_url + source_date required |
| CSV importer with row-level validation | ✅ | rejects missing provenance, bad coords |
| Deduplication on (name, lat, lon) | ✅ | |
| Path confinement to data/rest_facilities/ | ✅ | |
| Template + sourcing guide | ✅ | no fabricated rows |
| Distance via existing OSRM routing | ✅ | falls back to haversine with marker |
| Facility suggestion on WAIT / REPOSITION | ✅ | annotation, not a new decision |
| Only erified facilities suggested | ✅ | pending rows ignored |
| Frontend map markers | 🟡 | Requires facility data to be imported first |
| Live availability (parking, dormitory) | 🔵 | No public data source |
| Facility ratings / amenities API | 🔵 | Out of scope |

## 3. Decision engine integration

| Item | Status |
|---|---|
| Driver feasibility as an input to decision | ✅ |
| ASSIGN_NOW downgraded to REVIEW for infeasible driver | ✅ |
| driver_feasibility field in every response | ✅ |
| est_facility_suggestion field on WAIT / REPOSITION | ✅ |
| Backward compatibility (no driver = unchanged behaviour) | ✅ |
| No fifth decision category | ✅ |

## 4. Explainability

| Item | Status |
|---|---|
| SHAP drivers on ML predictions | ✅ (pre-existing, unchanged) |
| Cost breakdown per route | ✅ (pre-existing) |
| driver_feasibility reason string | ✅ |
| est_facility_suggestion reason string | ✅ |
| Clear separation of hard constraints vs heuristics | ✅ in response shape |
| Frontend panel to display driver + facility fields | 🟡 |

## 5. External search (internal-first, external-second)

| Item | Status |
|---|---|
| Internal-first matching (existing) | ✅ |
| Structured search-brief generation | 🟡 |
| BlackBuck / Vahak / Intugine API integration | 🔵 — explicitly NOT claimed |

## 6. Testing

| Metric | Value |
|---|---|
| Total tests (this branch) | **115** |
| Tests added since audit | 43 |
| Passing | 115 |
| Regressions vs pre-audit suite | 0 |

## 7. Documentation

| Item | Status |
|---|---|
| Architecture update (docs/architecture_update.md) | ✅ this commit |
| Assumptions & provenance (docs/assumptions.md) | ✅ this commit |
| Driver & facility design notes | ✅ this commit |
| Presentation summary (this doc) | ✅ this commit |
| Evaluation plan (docs/evaluation_plan.md) | ✅ this commit |
| README feature-status section | ✅ this commit |
| Demo video | 🟡 |
| Live deployment | 🔵 (deliberately local-only for this submission) |

## 8. Things this project does NOT claim

- **No fabricated GPS data.** Trucks move only via user-triggered simulation.
- **No live facility availability.** The system never asserts a facility is
  currently open or has space.
- **No legal compliance.** Driver rules are marked unverified.
- **No external API integration.** Internal search only.
- **No measured emissions.** CO2 is modelled.
- **No production telemetry.** GPS is simulated.
- **No real customer data.** All shipment pools are synthetic.

## 9. What would move this to "production-ready"

Not required for viva. Listed for completeness:

- Real telematics integration
- Jurisdiction-verified driving-hour rules with legal sign-off
- Live facility availability (would require NHAI partnership)
- Authentication hardening (refresh rotation, rate limiting)
- CI/CD pipeline with coverage gate
- Observability (structured logs, metrics, alerts)
- Cloud deployment with secrets management
