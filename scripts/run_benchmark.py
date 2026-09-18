'''Run the 4-way benchmark and save a JSON report.'''

import argparse
import json
from datetime import datetime
from pathlib import Path

from backend.database.connection import SessionLocal
from backend.services.benchmark import benchmark_fleet


REPORTS_DIR = Path("reports")


def print_table(results: dict) -> None:
    header = (
        f"{'Strategy':<18} "
        f"{'Trucks':>7} "
        f"{'Dist (km)':>12} "
        f"{'Cost (INR)':>15} "
        f"{'Profit (INR)':>15} "
        f"{'CO2 (kg)':>12}"
    )
    print(header)
    print("-" * len(header))

    for name, data in results.items():
        m = data["metrics"]
        print(
            f"{name:<18} "
            f"{m['trucks_assigned']:>7} "
            f"{m['total_distance_km']:>12,.1f} "
            f"{m['total_cost_inr']:>15,.0f} "
            f"{m['total_profit_inr']:>15,.0f} "
            f"{m['total_co2_kg']:>12,.1f}"
        )


def print_improvements(improvements: dict) -> None:
    print()
    print("AI improvements vs baselines:")
    for key, metrics in improvements.items():
        print(f"  {key}:")
        for metric, pct in metrics.items():
            sign = "+" if pct > 0 else ""
            print(f"    {metric:<26} {sign}{pct:.2f}%")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = (
        Path(args.output) if args.output
        else REPORTS_DIR / f"benchmark_{timestamp}.json"
    )

    db = SessionLocal()
    try:
        result = benchmark_fleet(db)
    finally:
        db.close()

    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, default=str)

    print("=" * 82)
    print("FLEET BENCHMARK - 4 STRATEGIES")
    print("=" * 82)
    print(f"Trucks evaluated      : {result['trucks_evaluated']}")
    print(f"Candidates considered : {result['candidates_considered']}")
    print()
    print_table(result["results"])
    print_improvements(result["improvements"])
    print()
    print(f"Report saved to: {out_path}")


if __name__ == "__main__":
    main()
