"""
Tests for pit-stop execution, duration formulas, and Safety Car discounts.
"""

import pytest
import random
from engine.pit_stop import calculate_pit_stop_duration


def test_pit_stop_duration_formula():
    """Total time must reflect transit loss, stationary servicing, and crew execution."""
    rng = random.Random(42)
    base_loss = 22.5
    res = calculate_pit_stop_duration(
        base_pit_lane_loss_s=base_loss,
        new_compound="MEDIUM",
        refuel_amount_kg=0.0,
        allow_refuelling=False,
        sc_discount_s=0.0,
        rng=rng,
    )

    # Stationary tyre change is ~2.45s +/- crew variance
    assert res.pit_lane_loss_s == 22.5
    assert res.tyre_change_time_s == 2.45
    assert res.refuel_time_s == 0.0
    assert 23.5 < res.total_pit_time_s < 26.5


def test_safety_car_pit_discount():
    """Under Safety Car, pit lane net time loss must be discounted."""
    rng = random.Random(99)
    res_green = calculate_pit_stop_duration(
        base_pit_lane_loss_s=22.5,
        new_compound="HARD",
        refuel_amount_kg=20.0,
        sc_discount_s=0.0,
        rng=rng,
    )

    rng2 = random.Random(99)
    res_sc = calculate_pit_stop_duration(
        base_pit_lane_loss_s=22.5,
        new_compound="HARD",
        refuel_amount_kg=20.0,
        sc_discount_s=10.5,
        rng=rng2,
    )

    saved_time = res_green.total_pit_time_s - res_sc.total_pit_time_s
    assert saved_time == pytest.approx(10.5, abs=0.2)
