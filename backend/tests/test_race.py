"""
Tests for full race loop determinism, telemetry invariants, and simulation completion.
"""

import pytest
from engine.race import RaceSimulation, RaceSimulationConfig


def test_race_simulation_determinism():
    """Identical seeds and configs must produce bit-for-bit identical race outcomes."""
    cfg1 = RaceSimulationConfig(seed=1337, total_laps=25, strategy_id="mdp_agent", scenario_name="changing_weather")
    sim1 = RaceSimulation(cfg1)
    snaps1, metrics1 = sim1.run_full_race()

    cfg2 = RaceSimulationConfig(seed=1337, total_laps=25, strategy_id="mdp_agent", scenario_name="changing_weather")
    sim2 = RaceSimulation(cfg2)
    snaps2, metrics2 = sim2.run_full_race()

    assert metrics1.total_race_time == metrics2.total_race_time
    assert metrics1.pit_stops == metrics2.pit_stops
    assert metrics1.final_position == metrics2.final_position
    assert len(snaps1) == len(snaps2)
    assert snaps1[-1]["car"]["fuel_kg"] == snaps2[-1]["car"]["fuel_kg"]


def test_race_feasible_plan_no_dnf():
    """MDP Agent must successfully complete a race without running out of fuel (DNF)."""
    cfg = RaceSimulationConfig(seed=42, total_laps=40, strategy_id="mdp_agent", scenario_name="dry_race")
    sim = RaceSimulation(cfg)
    _, metrics = sim.run_full_race()

    assert not metrics.dnf
    assert metrics.fuel_left_at_finish > 0.0
    assert metrics.pit_stops >= 1
