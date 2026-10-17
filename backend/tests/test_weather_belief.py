"""
Tests for Markov weather transitions and Bayesian forward belief filtering.
"""

import pytest
import random
from engine.weather import WeatherModel, WeatherObservation


def test_weather_belief_sums_to_one():
    """Bayesian belief probability distribution must strictly sum to 1.0 at every update."""
    model = WeatherModel(scenario_name="changing_weather", rng=random.Random(123))

    assert sum(model.belief.values()) == pytest.approx(1.0, abs=1e-3)

    for _ in range(30):
        _, obs = model.step_environment()
        belief, _ = model.bayesian_filter_update(obs)
        assert sum(belief.values()) == pytest.approx(1.0, abs=1e-3)
        for p in belief.values():
            assert 0.0 <= p <= 1.0


def test_weather_belief_converges_with_consistent_evidence():
    """Belief should converge strongly toward heavy rain given repeated heavy rain sensor observations."""
    model = WeatherModel(scenario_name="changing_weather", initial_state="DRY")

    # Feed repeated extreme rain evidence
    heavy_rain_obs = WeatherObservation(measured_grip=0.40, rain_sensor=0.92)
    for _ in range(5):
        belief, _ = model.bayesian_filter_update(heavy_rain_obs)

    assert belief["HEAVY_RAIN"] > 0.85, "Belief should strongly favor HEAVY_RAIN after persistent rain sensor readings"
    assert belief["DRY"] < 0.05
