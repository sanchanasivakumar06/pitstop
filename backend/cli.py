"""
Headless Command-Line Interface for the Race Strategist Engine.
Usage:
  python cli.py --strategy mdp_agent --laps 50 --scenario changing_weather
  python cli.py --compare --runs 20 --export results.json
"""

import argparse
import json
import sys
from typing import Any

from engine.race import RaceSimulation, RaceSimulationConfig
from engine.batch import run_batch_evaluation
from engine.tyres import TyreCompound


def main():
    parser = argparse.ArgumentParser(description="The Impossible Pit Stop - Race Strategist CLI")
    parser.add_argument("--seed", type=int, default=42, help="Simulation seed for determinism")
    parser.add_argument("--track", type=str, default="silverstone_classic", help="Track id (monza_sprint, silverstone_classic, spa_endurance)")
    parser.add_argument("--laps", type=int, default=50, help="Total race laps")
    parser.add_argument("--strategy", type=str, default="mdp_agent", help="Strategy to simulate")
    parser.add_argument("--scenario", type=str, default="changing_weather", help="Scenario preset name")
    parser.add_argument("--runs", type=int, default=10, help="Number of races in batch comparison")
    parser.add_argument("--compare", action="store_true", help="Run batch comparison across all strategies")
    parser.add_argument("--export", type=str, default=None, help="Export output file path (json/csv)")

    args = parser.parse_args()

    if args.compare:
        print(f"\n=======================================================")
        print(f" BATCH EVALUATION: {args.runs} Paired-Seed Races")
        print(f" Track: {args.track} | Laps: {args.laps}")
        print(f"=======================================================\n")
        results = run_batch_evaluation(
            n_races=args.runs,
            track_id=args.track,
            total_laps=args.laps,
        )

        header = f"{'Strategy':<18} | {'Mean Time':<10} | {'Std':<6} | {'Win Rate':<9} | {'Saved (s)':<10} | {'Stops':<6} | {'Consistency':<11}"
        print(header)
        print("-" * len(header))
        for row in results["summary"]:
            print(
                f"{row['strategy']:<18} | {row['mean']:<10.1f} | {row['std']:<6.1f} | "
                f"{str(row['win_rate']) + '%':<9} | {row['time_saved']:<10.1f} | {row['avg_pit_stops']:<6.1f} | "
                f"{str(row['consistency']) + '%':<11}"
            )
        print("\n")

        if args.export:
            with open(args.export, "w") as f:
                json.dump(results, f, indent=2)
            print(f"Saved batch results to {args.export}")

    else:
        print(f"\n=======================================================")
        print(f" SINGLE RACE SIMULATION: {args.strategy}")
        print(f" Track: {args.track} | Laps: {args.laps} | Scenario: {args.scenario} | Seed: {args.seed}")
        print(f"=======================================================\n")
        config = RaceSimulationConfig(
            seed=args.seed,
            track_id=args.track,
            total_laps=args.laps,
            strategy_id=args.strategy,
            scenario_name=args.scenario,
        )
        sim = RaceSimulation(config)
        snapshots, metrics = sim.run_full_race()

        print(f"Finished in:      {metrics.total_race_time:.2f} s")
        print(f"Final Position:   P{metrics.final_position}")
        print(f"Pit Stops:        {metrics.pit_stops} stops (Total time loss: {metrics.pit_time_total:.1f} s)")
        print(f"Average Lap Time: {metrics.avg_lap_time:.2f} s")
        print(f"Fuel Left:        {metrics.fuel_left_at_finish:.2f} kg (Used: {metrics.fuel_used:.2f} kg)")
        print(f"Replans:          {metrics.replans}")
        print(f"DNF:              {metrics.dnf}\n")

        if args.export:
            with open(args.export, "w") as f:
                json.dump({"metrics": metrics.to_dict(), "snapshots": snapshots}, f, indent=2)
            print(f"Exported race snapshots to {args.export}")


if __name__ == "__main__":
    main()
