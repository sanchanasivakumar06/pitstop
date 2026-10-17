"""
Markov weather chain simulation and Bayesian forward belief filtering.
Implements Hidden Markov Model (HMM) filtering with noisy sensor observations.
"""

from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

WEATHER_STATES = ["DRY", "LIGHT_RAIN", "HEAVY_RAIN"]

# Default transition matrices for scenario presets
# P(W_{t+1} | W_t) [current_state][next_state]
TRANSITION_MATRICES: Dict[str, Dict[str, Dict[str, float]]] = {
    "dry_race": {
        "DRY": {"DRY": 0.97, "LIGHT_RAIN": 0.03, "HEAVY_RAIN": 0.00},
        "LIGHT_RAIN": {"DRY": 0.40, "LIGHT_RAIN": 0.55, "HEAVY_RAIN": 0.05},
        "HEAVY_RAIN": {"DRY": 0.20, "LIGHT_RAIN": 0.60, "HEAVY_RAIN": 0.20},
    },
    "changing_weather": {
        "DRY": {"DRY": 0.82, "LIGHT_RAIN": 0.15, "HEAVY_RAIN": 0.03},
        "LIGHT_RAIN": {"DRY": 0.18, "LIGHT_RAIN": 0.64, "HEAVY_RAIN": 0.18},
        "HEAVY_RAIN": {"DRY": 0.05, "LIGHT_RAIN": 0.40, "HEAVY_RAIN": 0.55},
    },
    "wet_race": {
        "DRY": {"DRY": 0.20, "LIGHT_RAIN": 0.50, "HEAVY_RAIN": 0.30},
        "LIGHT_RAIN": {"DRY": 0.05, "LIGHT_RAIN": 0.45, "HEAVY_RAIN": 0.50},
        "HEAVY_RAIN": {"DRY": 0.02, "LIGHT_RAIN": 0.28, "HEAVY_RAIN": 0.70},
    },
    "safety_car_heavy": {
        "DRY": {"DRY": 0.88, "LIGHT_RAIN": 0.10, "HEAVY_RAIN": 0.02},
        "LIGHT_RAIN": {"DRY": 0.20, "LIGHT_RAIN": 0.65, "HEAVY_RAIN": 0.15},
        "HEAVY_RAIN": {"DRY": 0.05, "LIGHT_RAIN": 0.45, "HEAVY_RAIN": 0.50},
    },
    "high_degradation": {
        "DRY": {"DRY": 0.95, "LIGHT_RAIN": 0.05, "HEAVY_RAIN": 0.00},
        "LIGHT_RAIN": {"DRY": 0.35, "LIGHT_RAIN": 0.60, "HEAVY_RAIN": 0.05},
        "HEAVY_RAIN": {"DRY": 0.15, "LIGHT_RAIN": 0.60, "HEAVY_RAIN": 0.25},
    },
}

# Sensor observation parameters: (mean_grip, std_grip, mean_rain_sensor, std_rain_sensor)
SENSOR_PROFILES: Dict[str, Tuple[float, float, float, float]] = {
    "DRY": (0.95, 0.04, 0.05, 0.05),
    "LIGHT_RAIN": (0.72, 0.06, 0.45, 0.10),
    "HEAVY_RAIN": (0.45, 0.08, 0.85, 0.08),
}


def _gaussian_pdf(x: float, mean: float, std: float) -> float:
    var = std * std
    denom = math.sqrt(2.0 * math.pi * var)
    num = math.exp(-((x - mean) ** 2) / (2.0 * var))
    return max(1e-6, num / denom)


@dataclass
class WeatherObservation:
    measured_grip: float      # e.g. 0.93 in dry, 0.68 in light rain, 0.42 in heavy rain
    rain_sensor: float        # e.g. 0.02 in dry, 0.48 in light rain, 0.88 in heavy rain


class WeatherModel:
    """
    Simulates environment weather transitions and computes Bayesian belief updates.
    """

    def __init__(
        self,
        scenario_name: str = "changing_weather",
        initial_state: str = "DRY",
        rng: random.Random | None = None,
    ):
        self.scenario_name = scenario_name
        self.transitions = TRANSITION_MATRICES.get(scenario_name, TRANSITION_MATRICES["changing_weather"])
        self.current_state = initial_state
        self.rng = rng or random.Random(42)

        # Agent's initial belief distribution
        if initial_state == "DRY":
            self.belief: Dict[str, float] = {"DRY": 0.90, "LIGHT_RAIN": 0.08, "HEAVY_RAIN": 0.02}
        elif initial_state == "LIGHT_RAIN":
            self.belief = {"DRY": 0.10, "LIGHT_RAIN": 0.80, "HEAVY_RAIN": 0.10}
        else:
            self.belief = {"DRY": 0.05, "LIGHT_RAIN": 0.25, "HEAVY_RAIN": 0.70}

        self.track_temp_c = 32.0 if initial_state == "DRY" else 22.0
        self.current_grip = 0.96 if initial_state == "DRY" else 0.72

    def step_environment(self) -> Tuple[str, WeatherObservation]:
        """
        Advances the true hidden weather state using the Markov transition matrix,
        and generates noisy sensor readings.
        """
        trans = self.transitions[self.current_state]
        r = self.rng.random()
        cumulative = 0.0
        new_state = self.current_state

        for candidate, prob in trans.items():
            cumulative += prob
            if r <= cumulative:
                new_state = candidate
                break

        self.current_state = new_state

        # Update environment physical properties
        target_temp = {"DRY": 33.0, "LIGHT_RAIN": 22.0, "HEAVY_RAIN": 17.0}[self.current_state]
        self.track_temp_c += (target_temp - self.track_temp_c) * 0.25

        target_grip = {"DRY": 0.96, "LIGHT_RAIN": 0.72, "HEAVY_RAIN": 0.46}[self.current_state]
        self.current_grip += (target_grip - self.current_grip) * 0.35

        # Generate noisy observations
        m_grip, s_grip, m_rain, s_rain = SENSOR_PROFILES[self.current_state]
        measured_grip = max(0.2, min(1.0, self.rng.gauss(m_grip, s_grip)))
        rain_sensor = max(0.0, min(1.0, self.rng.gauss(m_rain, s_rain)))

        return self.current_state, WeatherObservation(measured_grip, rain_sensor)

    def bayesian_filter_update(
        self,
        observation: WeatherObservation,
    ) -> Tuple[Dict[str, float], Dict[str, Any]]:
        """
        HMM Forward update:
        1. Predict: P(W_t = s) = sum_{s'} P(s | s') * P(W_{t-1} = s')
        2. Update: P(W_t = s | O_t) = alpha * P(O_t | s) * P(W_t = s)
        Returns the updated normalized belief and detailed calculation explanation.
        """
        # Step 1: Predict (Time update / Prior)
        predicted_prior: Dict[str, float] = {}
        for target_state in WEATHER_STATES:
            prior_sum = sum(
                self.belief[prev_state] * self.transitions[prev_state][target_state]
                for prev_state in WEATHER_STATES
            )
            predicted_prior[target_state] = prior_sum

        # Step 2: Compute observation likelihoods P(O_t | s)
        likelihoods: Dict[str, float] = {}
        for s in WEATHER_STATES:
            m_grip, s_grip, m_rain, s_rain = SENSOR_PROFILES[s]
            p_grip = _gaussian_pdf(observation.measured_grip, m_grip, s_grip)
            p_rain = _gaussian_pdf(observation.rain_sensor, m_rain, s_rain)
            likelihoods[s] = p_grip * p_rain

        # Step 3: Unnormalized posterior
        raw_posterior = {
            s: predicted_prior[s] * likelihoods[s]
            for s in WEATHER_STATES
        }
        total_evidence = sum(raw_posterior.values()) or 1e-6

        # Step 4: Normalize
        updated_belief = {
            s: round(raw_posterior[s] / total_evidence, 4)
            for s in WEATHER_STATES
        }
        # Guarantee exact 1.0 sum
        diff = 1.0 - sum(updated_belief.values())
        updated_belief[self.current_state] = round(updated_belief[self.current_state] + diff, 4)

        self.belief = updated_belief

        explanation = {
            "id": "weather_belief",
            "title": "Bayesian Weather Belief Update",
            "formula": "Belief(s_t) = alpha * P(Obs | s_t) * sum_{s_{t-1}} [ P(s_t | s_{t-1}) * Belief(s_{t-1}) ]",
            "inputs": {
                "measured_grip": round(observation.measured_grip, 3),
                "rain_sensor": round(observation.rain_sensor, 3),
            },
            "steps": [
                f"1. Prior prediction after transition model: DRY={predicted_prior['DRY']:.3f}, LIGHT={predicted_prior['LIGHT_RAIN']:.3f}, HEAVY={predicted_prior['HEAVY_RAIN']:.3f}",
                f"2. Observation likelihoods: DRY={likelihoods['DRY']:.2f}, LIGHT={likelihoods['LIGHT_RAIN']:.2f}, HEAVY={likelihoods['HEAVY_RAIN']:.2f}",
                f"3. Total evidence alpha = {total_evidence:.4f}",
            ],
            "result": f"Belief: DRY={self.belief['DRY']*100:.1f}%, LIGHT_RAIN={self.belief['LIGHT_RAIN']*100:.1f}%, HEAVY_RAIN={self.belief['HEAVY_RAIN']*100:.1f}%",
            "plain_english": f"Based on track grip ({observation.measured_grip:.2f}) and rain sensor ({observation.rain_sensor:.2f}), the AI is {max(self.belief.values())*100:.1f}% confident the condition is {max(self.belief, key=self.belief.get)}.",
        }

        return self.belief, explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "true_state": self.current_state,
            "belief": {k: round(v, 3) for k, v in self.belief.items()},
            "track_temp_c": round(self.track_temp_c, 1),
            "grip": round(self.current_grip, 2),
        }
