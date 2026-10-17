"""
Tests for Utility Theory and Maximum Expected Utility (MEU) decision making.
"""

import pytest
from engine.agent.percepts import Percepts, Action
from engine.agent.utility import evaluate_action_utility, select_best_action_utility
from engine.tyres import TyreCompound


def test_utility_terms_add_up_to_net_utility():
    """All 6 decomposed utility terms must sum to the net utility score."""
    percepts = Percepts(
        lap=25,
        total_laps=60,
        fuel_kg=40.0,
        tyre_compound=TyreCompound.MEDIUM,
        tyre_wear_pct=65.0,
        tyre_age_laps=25,
        track_temp_c=30.0,
        gap_ahead_s=2.5,
        gap_behind_s=1.2,
        weather_belief={"DRY": 0.9, "LIGHT_RAIN": 0.1, "HEAVY_RAIN": 0.0},
        is_safety_car=False,
        is_vsc=False,
        has_puncture=False,
    )

    terms = evaluate_action_utility(Action.PIT_HARD, percepts)
    expected_cost = (
        terms.pit_time_loss
        - terms.tyre_pace_gain
        + terms.fuel_weight_gain
        + terms.wear_risk_penalty
        + terms.traffic_penalty
        + terms.weather_mismatch_penalty
    )

    assert terms.net_utility == pytest.approx(-expected_cost, abs=1e-2)


def test_meu_picks_action_with_highest_utility():
    """select_best_action_utility must select the action corresponding to max(utilities)."""
    percepts = Percepts(
        lap=20,
        total_laps=50,
        fuel_kg=50.0,
        tyre_compound=TyreCompound.MEDIUM,
        tyre_wear_pct=82.0,  # Highly degraded!
        tyre_age_laps=20,
        track_temp_c=30.0,
        gap_ahead_s=5.0,
        gap_behind_s=3.0,
        weather_belief={"DRY": 0.95, "LIGHT_RAIN": 0.05, "HEAVY_RAIN": 0.0},
        is_safety_car=False,
        is_vsc=False,
        has_puncture=False,
    )

    best_action, _, utilities, _ = select_best_action_utility(percepts)
    max_util_action = max(utilities, key=utilities.get)

    assert best_action.value == max_util_action
    # High wear (82%) should motivate taking a pit stop rather than staying out
    assert best_action != Action.STAY_OUT


def test_utility_emergency_puncture_handling():
    """Punctured tyre must have massive wear risk penalty forcing an immediate stop."""
    percepts = Percepts(
        lap=15,
        total_laps=60,
        fuel_kg=50.0,
        tyre_compound=TyreCompound.MEDIUM,
        tyre_wear_pct=25.0,
        tyre_age_laps=15,
        track_temp_c=30.0,
        gap_ahead_s=2.0,
        gap_behind_s=2.0,
        weather_belief={"DRY": 0.9, "LIGHT_RAIN": 0.1, "HEAVY_RAIN": 0.0},
        is_safety_car=False,
        is_vsc=False,
        has_puncture=True,
    )

    stay_out_terms = evaluate_action_utility(Action.STAY_OUT, percepts)
    pit_terms = evaluate_action_utility(Action.PIT_MEDIUM, percepts)

    assert stay_out_terms.wear_risk_penalty > 4000.0
    assert pit_terms.net_utility > stay_out_terms.net_utility
