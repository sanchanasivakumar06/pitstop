"""
Lap time simulation model with transparent term-by-term breakdown.
lap_time = base_lap + compound_offset + tyre_wear + fuel_weight + weather + traffic + pace_mode + noise
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Dict, Any

from engine.tyres import (
    TyreState,
    COMPOUND_SPECS,
    calculate_tyre_wear_penalty,
    calculate_weather_mismatch_penalty,
)
from engine.fuel import calculate_fuel_weight_penalty


@dataclass
class LapTimeBreakdown:
    total_lap_time_s: float
    base_lap_s: float
    compound_offset_s: float
    tyre_wear_penalty_s: float
    fuel_weight_penalty_s: float
    weather_penalty_s: float
    traffic_penalty_s: float
    pace_mode_delta_s: float
    event_delta_s: float
    noise_s: float

    def to_explanation(self) -> Dict[str, Any]:
        """Returns structured explanation data for the UI info button popover."""
        return {
            "id": "lap_time_breakdown",
            "title": "Lap Time Calculation",
            "formula": "T_lap = T_base + Delta_compound + Delta_wear + Delta_fuel + Delta_weather + Delta_traffic + Delta_pace + Delta_event + Noise",
            "inputs": {
                "base_lap_s": round(self.base_lap_s, 3),
                "compound_offset_s": round(self.compound_offset_s, 3),
                "tyre_wear_penalty_s": round(self.tyre_wear_penalty_s, 3),
                "fuel_weight_penalty_s": round(self.fuel_weight_penalty_s, 3),
                "weather_penalty_s": round(self.weather_penalty_s, 3),
                "traffic_penalty_s": round(self.traffic_penalty_s, 3),
                "pace_mode_delta_s": round(self.pace_mode_delta_s, 3),
                "event_delta_s": round(self.event_delta_s, 3),
                "noise_s": round(self.noise_s, 3),
            },
            "steps": [
                f"1. Base track benchmark: {self.base_lap_s:.2f} s",
                f"2. Tyre compound delta: {self.compound_offset_s:+.2f} s",
                f"3. Wear degradation: +{self.tyre_wear_penalty_s:.2f} s",
                f"4. Fuel weight (mass effect): +{self.fuel_weight_penalty_s:.2f} s",
                f"5. Weather suitability penalty: +{self.weather_penalty_s:.2f} s",
                f"6. Traffic / dirty air: +{self.traffic_penalty_s:.2f} s",
                f"7. Pace mode adjustment: {self.pace_mode_delta_s:+.2f} s",
                f"8. Race event neutralizations: +{self.event_delta_s:.2f} s",
                f"9. Execution variance / noise: {self.noise_s:+.2f} s",
            ],
            "result": f"{self.total_lap_time_s:.2f} s",
            "plain_english": f"Lap time totaled {self.total_lap_time_s:.2f}s, influenced predominantly by wear (+{self.tyre_wear_penalty_s:.2f}s) and weather (+{self.weather_penalty_s:.2f}s).",
        }


def calculate_lap_time(
    base_lap_s: float,
    tyre: TyreState,
    fuel_kg: float,
    weather_state: str,
    pace_mode: str,
    gap_ahead_s: float,
    event_delta_s: float = 0.0,
    rng: random.Random | None = None,
) -> LapTimeBreakdown:
    """
    Computes lap time and returns the exact breakdown of all constituents.
    """
    spec = COMPOUND_SPECS[tyre.compound]
    compound_offset = spec.base_pace_delta_s

    # Tyre wear degradation
    wear_penalty = calculate_tyre_wear_penalty(tyre)

    # Fuel weight penalty (0.033 s/kg)
    fuel_penalty = calculate_fuel_weight_penalty(fuel_kg)

    # Weather mismatch
    weather_penalty = calculate_weather_mismatch_penalty(tyre.compound, weather_state)

    # Traffic penalty: if trailing another car within 1.2s dirty air window
    traffic_penalty = 0.0
    if 0.0 < gap_ahead_s < 1.4:
        # Dirty air disrupts aerodynamics and reduces cornering grip
        traffic_penalty = max(0.0, (1.4 - gap_ahead_s) * 0.75)

    # Pace mode delta
    pace_delta = {
        "PUSH": -0.65,
        "NORMAL": 0.00,
        "CONSERVE": 0.80,
    }.get(pace_mode, 0.0)

    # Driver/lap noise
    noise = 0.0
    if rng:
        noise = rng.gauss(0.0, 0.12)

    total_lap = (
        base_lap_s
        + compound_offset
        + wear_penalty
        + fuel_penalty
        + weather_penalty
        + traffic_penalty
        + pace_delta
        + event_delta_s
        + noise
    )

    return LapTimeBreakdown(
        total_lap_time_s=max(10.0, round(total_lap, 3)),
        base_lap_s=base_lap_s,
        compound_offset_s=compound_offset,
        tyre_wear_penalty_s=wear_penalty,
        fuel_weight_penalty_s=fuel_penalty,
        weather_penalty_s=weather_penalty,
        traffic_penalty_s=traffic_penalty,
        pace_mode_delta_s=pace_delta,
        event_delta_s=event_delta_s,
        noise_s=noise,
    )
