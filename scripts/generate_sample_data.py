"""
Generates deterministic pre-computed sample data files for offline demo mode and benchmarks.
Outputs:
  - sample_data/snapshots_demo.json
  - sample_data/comparison_demo.json
"""

import json
import os
import sys

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from engine.race import RaceSimulation, RaceSimulationConfig
from engine.batch import run_batch_evaluation
from engine.tyres import TyreCompound


def generate_sample_data():
    sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sample_data'))
    os.makedirs(sample_dir, exist_ok=True)

    print("Generating demo snapshots with fixed seed 42...")
    config = RaceSimulationConfig(
        seed=42,
        track_id="silverstone_classic",
        total_laps=50,
        strategy_id="mdp_agent",
        scenario_name="changing_weather",
        start_fuel_kg=65.0,
        start_tyre_compound=TyreCompound.MEDIUM,
    )
    sim = RaceSimulation(config)
    snapshots, metrics = sim.run_full_race()

    snapshots_path = os.path.join(sample_dir, "snapshots_demo.json")
    with open(snapshots_path, "w", encoding="utf-8") as f:
        json.dump(snapshots, f, indent=2)
    print(f"-> Saved {len(snapshots)} snapshots to {snapshots_path}")

    print("Generating 20-race batch comparison data across all scenarios...")
    comparison_results = run_batch_evaluation(
        strategies=["mdp_agent", "utility_agent", "reactive_rules", "baseline_fixed"],
        scenarios=["dry_race", "changing_weather", "wet_race", "safety_car_heavy", "high_degradation"],
        n_races=20,
        track_id="silverstone_classic",
        total_laps=40,
    )

    comparison_path = os.path.join(sample_dir, "comparison_demo.json")
    with open(comparison_path, "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=2)
    print(f"-> Saved multi-race comparison results to {comparison_path}")


if __name__ == "__main__":
    generate_sample_data()
