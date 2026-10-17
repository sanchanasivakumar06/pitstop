"""
Tests for Markov Decision Process (MDP) and Dynamic Programming backward induction.
"""

import time
import pytest
from engine.agent.mdp import MDPSolver
from engine.agent.percepts import Percepts, Action
from engine.tyres import TyreCompound


def test_mdp_solve_performance_under_50ms():
    """MDPSolver backward induction must solve within the 50 ms budget."""
    solver = MDPSolver(total_laps=50, base_lap_s=88.5, base_pit_loss_s=22.5)
    t0 = time.perf_counter()
    solver.solve(start_lap=0)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 50.0, f"MDP solve took {elapsed_ms:.1f}ms (must be < 50ms)"


def test_mdp_final_lap_optimality():
    """On the final lap (total_laps - 1), STAY_OUT must strictly dominate pitting because pit loss cannot be amortized."""
    total_laps = 50
    solver = MDPSolver(total_laps=total_laps, base_lap_s=88.5, base_pit_loss_s=22.5)
    solver.solve(start_lap=total_laps - 1)

    percepts = Percepts(
        lap=total_laps - 1,
        total_laps=total_laps,
        fuel_kg=25.0,
        tyre_compound=TyreCompound.MEDIUM,
        tyre_wear_pct=40.0,
        tyre_age_laps=10,
        track_temp_c=30.0,
        gap_ahead_s=2.0,
        gap_behind_s=2.0,
        weather_belief={"DRY": 1.0, "LIGHT_RAIN": 0.0, "HEAVY_RAIN": 0.0},
        is_safety_car=False,
        is_vsc=False,
        has_puncture=False,
    )

    q_vals = solver.get_action_q_values(percepts)
    stay_out_q = q_vals["STAY_OUT"]
    pit_q = q_vals["PIT_MEDIUM"]

    # STAY_OUT should save more than 20 seconds compared to pitting on the final lap
    assert stay_out_q < pit_q - 20.0
