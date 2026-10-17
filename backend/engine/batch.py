"""
Multi-race and multi-scenario batch evaluation engine.
Executes paired-seed Monte Carlo evaluations comparing AI strategies against baselines.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from engine.race import RaceSimulation, RaceSimulationConfig
from engine.metrics import RaceMetrics, BatchMetrics, compute_batch_statistics
from engine.tyres import TyreCompound

DEFAULT_SCENARIOS = [
    "dry_race",
    "changing_weather",
    "wet_race",
    "safety_car_heavy",
    "high_degradation",
]


def run_batch_evaluation(
    strategies: List[str] | None = None,
    scenarios: List[str] | None = None,
    n_races: int = 20,
    seeds: List[int] | None = None,
    track_id: str = "silverstone_classic",
    total_laps: int = 50,
) -> Dict[str, Any]:
    """
    Runs multi-race batch evaluation across requested strategies and scenarios with paired seeds.
    Returns comparison summary and detailed per-race rows.
    """
    if not strategies:
        strategies = ["mdp_agent", "utility_agent", "reactive_rules", "baseline_fixed"]
    if not scenarios:
        scenarios = DEFAULT_SCENARIOS

    if not seeds:
        seeds = [1000 + i for i in range(n_races)]
    else:
        n_races = len(seeds)

    # Distribute scenarios cyclically across the seeds
    race_scenarios = [scenarios[i % len(scenarios)] for i in range(n_races)]

    # Collect race metrics per strategy: strategy_id -> list of RaceMetrics
    strategy_results: Dict[str, List[RaceMetrics]] = {s: [] for s in strategies}
    per_race_records: List[Dict[str, Any]] = []

    # Run paired simulations: for each seed and scenario, run all strategies
    for idx, (seed, scenario) in enumerate(zip(seeds, race_scenarios)):
        race_record = {
            "race_index": idx + 1,
            "seed": seed,
            "scenario": scenario,
            "results": {},
        }

        for strategy_id in strategies:
            config = RaceSimulationConfig(
                seed=seed,
                track_id=track_id,
                total_laps=total_laps,
                strategy_id=strategy_id,
                scenario_name=scenario,
                start_fuel_kg=65.0,
                start_tyre_compound=TyreCompound.MEDIUM if scenario != "wet_race" else TyreCompound.INTERMEDIATE,
            )
            sim = RaceSimulation(config)
            _, metrics = sim.run_full_race()
            strategy_results[strategy_id].append(metrics)
            race_record["results"][strategy_id] = {
                "total_time": metrics.total_race_time,
                "pit_stops": metrics.pit_stops,
                "position": metrics.final_position,
                "dnf": metrics.dnf,
            }

        per_race_records.append(race_record)

    # Compute batch statistics relative to baseline_fixed (or the last listed strategy)
    baseline_strat = "baseline_fixed" if "baseline_fixed" in strategies else strategies[-1]
    baseline_metrics = strategy_results.get(baseline_strat, [])

    summary_list: List[Dict[str, Any]] = []
    for strategy_id in strategies:
        batch_stat = compute_batch_statistics(
            strategy_name=strategy_id,
            race_results=strategy_results[strategy_id],
            baseline_results=baseline_metrics if strategy_id != baseline_strat else None,
            scenario_tags=race_scenarios,
        )
        summary_list.append(batch_stat.to_dict())

    return {
        "n_races": n_races,
        "scenarios": scenarios,
        "strategies": strategies,
        "baseline": baseline_strat,
        "summary": summary_list,
        "per_race": per_race_records,
    }
