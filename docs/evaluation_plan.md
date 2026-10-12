# Evaluation Plan — Future Controlled Study

**This is a plan. No experimental results are claimed.** Existing benchmark
(scripts/run_benchmark.py) is a starting point; this document defines the
fuller study that would follow.

---

## 1. Objective

Measure the marginal contribution of each added component (ML predictions,
optimization, driver constraints, CO2-aware scoring) to operational
outcomes, on identical scenarios.

## 2. Strategies to compare

| Label | Description |
|---|---|
| **NN** | Nearest-neighbour: pick the shipment with the smallest pickup distance |
| **GP** | Greedy-profit: pick the highest-revenue shipment |
| **OT-Rules** | OR-Tools assignment using rule-based match_score only |
| **AI-NoDriver** | Full pipeline, but ignoring driver feasibility |
| **AI-NoCO2** | Full pipeline, but CO2 shadow price set to zero |
| **AI-Full** | Full pipeline: ML + optimizer + driver + CO2 |

## 3. Scenario pool

- **N = 50 shipments** per scenario, drawn across 14 cities
- **Trucks:** varied set of available trucks, at least 3 in different cities
- **Reproducibility:** fixed seed (--seed 42) per scenario
- **Repeat:** 5 scenarios with different seeds to smooth variance

## 4. Metrics

Per strategy, aggregated across trucks and shipments:

| Metric | Unit | Notes |
|---|---|---|
| Backhaul assignment rate | % | assigned / available trucks |
| Empty kilometres | km | total pickup distance for assigned trips |
| Total operating cost | INR | from cost model |
| Total profit | INR | revenue − cost |
| Estimated CO2 | kg | from emission model |
| Waiting time | hours | from ML prediction, summed |
| Capacity utilisation | % | weighted by shipment weight |
| Runtime | seconds | wall-clock for the decision pass |

## 5. Ablation design

The ablation isolates each component by turning it off:

| Ablation | What changes | What it shows |
|---|---|---|
| AI-Full → AI-NoML | ML context replaced with 0 adjustment | Value of the ML layer |
| AI-Full → AI-NoCO2 | CO2 shadow price = 0 | Value of carbon-aware scoring |
| AI-Full → AI-NoDriver | Driver feasibility check bypassed | Value of driver constraints |
| AI-Full → AI-RulesOnly | Skip OR-Tools, use top-1 by match score | Value of optimization |

Each ablation reports the same metrics as the main comparison.

## 6. Statistical treatment

- Report median and interquartile range across the 5 seeds.
- Use a paired test (Wilcoxon signed-rank) comparing each strategy against
  AI-Full on the same scenario set.
- Do not report a single number as "the improvement" — report the
  distribution.

## 7. Known limitations of this plan

- **Synthetic shipment pool.** Differences are attributable to the decision
  logic, not to real freight markets.
- **Simulated GPS.** Travel times come from the routing model, not from
  observed trips.
- **Small sample.** 5 scenarios is enough to show directional differences,
  not to establish statistical significance at high confidence.
- **No adversarial cases** (fuel-price spikes, strikes, road closures).
  Future work could add these.

## 8. What this plan is NOT

- Not a claim of real-world improvement
- Not a legal or operational audit
- Not a substitute for a live pilot
- Not to be reported without running the actual experiments

## 9. How to run the current (partial) version

    python -m scripts.reset_benchmark_state
    python -m scripts.seed_benchmark_shipments --count 50 --clear --seed 42
    python -m scripts.run_benchmark

Reports are written to eports/benchmark_<timestamp>.json.

The current benchmark implements NN / GP / OT-Rules / AI (4 strategies).
Extending it to the 6-strategy ablation above is a future task.
