"""
Tests for tyre wear degradation, cliff effect, and fuel consumption invariants.
"""

import pytest
from engine.tyres import (
    TyreCompound,
    TyreState,
    calculate_tyre_wear_delta,
    calculate_tyre_wear_penalty,
    COMPOUND_SPECS,
)
from engine.fuel import (
    FuelState,
    calculate_fuel_consumption,
    calculate_fuel_weight_penalty,
)


def test_tyre_wear_monotonic_growth():
    """Tyre wear must monotonically increase over successive laps under positive stress."""
    state = TyreState(compound=TyreCompound.MEDIUM, wear_pct=0.0)
    wear_history = [state.wear_pct]

    for _ in range(15):
        delta = calculate_tyre_wear_delta(state.compound, "NORMAL", 30.0, "DRY")
        assert delta > 0.0
        state.wear_pct += delta
        state.age_laps += 1
        wear_history.append(state.wear_pct)

    for i in range(len(wear_history) - 1):
        assert wear_history[i] < wear_history[i + 1]


def test_tyre_cliff_penalty_escalation():
    """Penalty rate must escalate quadratically beyond the compound's cliff threshold."""
    compound = TyreCompound.MEDIUM
    spec = COMPOUND_SPECS[compound]
    cliff = spec.cliff_threshold_pct

    # Before cliff
    t_pre1 = TyreState(compound=compound, wear_pct=cliff - 15.0)
    t_pre2 = TyreState(compound=compound, wear_pct=cliff - 5.0)
    pen_pre1 = calculate_tyre_wear_penalty(t_pre1)
    pen_pre2 = calculate_tyre_wear_penalty(t_pre2)
    delta_pre = pen_pre2 - pen_pre1

    # Beyond cliff (same 10% wear step)
    t_post1 = TyreState(compound=compound, wear_pct=cliff + 5.0)
    t_post2 = TyreState(compound=compound, wear_pct=cliff + 15.0)
    pen_post1 = calculate_tyre_wear_penalty(t_post1)
    pen_post2 = calculate_tyre_wear_penalty(t_post2)
    delta_post = pen_post2 - pen_post1

    assert delta_post > delta_pre * 1.5, "Post-cliff degradation delta must sharply exceed pre-cliff linear rate"


def test_fuel_consumption_pace_hierarchy():
    """PUSH mode must burn strictly more fuel than NORMAL, and NORMAL strictly more than CONSERVE."""
    base = 1.75
    burn_push = calculate_fuel_consumption(base, "PUSH", "DRY")
    burn_norm = calculate_fuel_consumption(base, "NORMAL", "DRY")
    burn_cons = calculate_fuel_consumption(base, "CONSERVE", "DRY")

    assert burn_push > burn_norm
    assert burn_norm > burn_cons


def test_fuel_state_invariants():
    """Fuel level must remain non-negative and correctly report range."""
    fuel = FuelState(fuel_kg=10.0, capacity_kg=105.0)
    assert fuel.percentage == pytest.approx(9.5, 0.1)
    assert fuel.laps_remaining(2.0) == 5.0

    # Test weight penalty formula
    pen_60kg = calculate_fuel_weight_penalty(60.0)
    pen_10kg = calculate_fuel_weight_penalty(10.0)
    assert pen_60kg > pen_10kg
    assert pen_60kg == pytest.approx(60.0 * 0.033, 0.01)
