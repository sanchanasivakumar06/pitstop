"""
Tyre compound characteristics, wear dynamics, and grip models.
Models non-linear degradation ("cliff"), temperature windows, and wet/dry suitability.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Any


class TyreCompound(str, Enum):
    SOFT = "SOFT"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    INTERMEDIATE = "INTERMEDIATE"
    WET = "WET"


@dataclass(frozen=True)
class CompoundSpec:
    compound: TyreCompound
    base_pace_delta_s: float     # Pace offset relative to MEDIUM on dry track (negative is faster)
    base_wear_rate_pct: float    # Base percentage wear per lap under normal conditions
    cliff_threshold_pct: float   # Wear percentage where performance degradation spikes sharply
    linear_deg_s: float          # Lap time degradation per 10% wear before the cliff
    cliff_deg_factor: float      # Multiplier for squared wear delta beyond the cliff
    optimal_temp_c: float        # Optimal track/tyre operating temperature
    temp_sensitivity: float      # Additional wear factor per degree away from optimal


COMPOUND_SPECS: Dict[TyreCompound, CompoundSpec] = {
    TyreCompound.SOFT: CompoundSpec(
        compound=TyreCompound.SOFT,
        base_pace_delta_s=-1.20,
        base_wear_rate_pct=5.50,
        cliff_threshold_pct=60.0,
        linear_deg_s=0.12,
        cliff_deg_factor=0.015,
        optimal_temp_c=32.0,
        temp_sensitivity=0.015,
    ),
    TyreCompound.MEDIUM: CompoundSpec(
        compound=TyreCompound.MEDIUM,
        base_pace_delta_s=0.00,
        base_wear_rate_pct=3.40,
        cliff_threshold_pct=70.0,
        linear_deg_s=0.08,
        cliff_deg_factor=0.012,
        optimal_temp_c=30.0,
        temp_sensitivity=0.012,
    ),
    TyreCompound.HARD: CompoundSpec(
        compound=TyreCompound.HARD,
        base_pace_delta_s=0.85,
        base_wear_rate_pct=2.10,
        cliff_threshold_pct=78.0,
        linear_deg_s=0.05,
        cliff_deg_factor=0.010,
        optimal_temp_c=28.0,
        temp_sensitivity=0.010,
    ),
    TyreCompound.INTERMEDIATE: CompoundSpec(
        compound=TyreCompound.INTERMEDIATE,
        base_pace_delta_s=3.20,
        base_wear_rate_pct=4.00,
        cliff_threshold_pct=65.0,
        linear_deg_s=0.09,
        cliff_deg_factor=0.014,
        optimal_temp_c=22.0,
        temp_sensitivity=0.020,
    ),
    TyreCompound.WET: CompoundSpec(
        compound=TyreCompound.WET,
        base_pace_delta_s=6.50,
        base_wear_rate_pct=3.80,
        cliff_threshold_pct=72.0,
        linear_deg_s=0.07,
        cliff_deg_factor=0.011,
        optimal_temp_c=18.0,
        temp_sensitivity=0.025,
    ),
}

# Suitability matrix: [Compound, WeatherState] -> suitability factor in [0.0, 1.0]
# 1.0 = optimal match. Slicks in heavy rain get 0.05, causing huge lap time penalties.
SUITABILITY: Dict[Tuple[TyreCompound, str], float] = {
    # DRY
    (TyreCompound.SOFT, "DRY"): 1.00,
    (TyreCompound.MEDIUM, "DRY"): 1.00,
    (TyreCompound.HARD, "DRY"): 1.00,
    (TyreCompound.INTERMEDIATE, "DRY"): 0.50,
    (TyreCompound.WET, "DRY"): 0.20,
    # LIGHT_RAIN
    (TyreCompound.SOFT, "LIGHT_RAIN"): 0.35,
    (TyreCompound.MEDIUM, "LIGHT_RAIN"): 0.35,
    (TyreCompound.HARD, "LIGHT_RAIN"): 0.30,
    (TyreCompound.INTERMEDIATE, "LIGHT_RAIN"): 1.00,
    (TyreCompound.WET, "LIGHT_RAIN"): 0.85,
    # HEAVY_RAIN
    (TyreCompound.SOFT, "HEAVY_RAIN"): 0.10,
    (TyreCompound.MEDIUM, "HEAVY_RAIN"): 0.10,
    (TyreCompound.HARD, "HEAVY_RAIN"): 0.08,
    (TyreCompound.INTERMEDIATE, "HEAVY_RAIN"): 0.65,
    (TyreCompound.WET, "HEAVY_RAIN"): 1.00,
}


@dataclass
class TyreState:
    compound: TyreCompound
    age_laps: int = 0
    wear_pct: float = 0.0       # 0% = new, 100% = completely worn/shredded
    temp_c: float = 30.0

    @property
    def grip_pct(self) -> float:
        """Remaining usable mechanical grip percentage (0..100%)."""
        return max(5.0, round(100.0 - (self.wear_pct * 0.95), 1))

    @property
    def is_past_cliff(self) -> bool:
        spec = COMPOUND_SPECS[self.compound]
        return self.wear_pct >= spec.cliff_threshold_pct

    def to_dict(self) -> Dict[str, Any]:
        return {
            "compound": self.compound.value,
            "age_laps": self.age_laps,
            "wear_pct": round(self.wear_pct, 1),
            "grip_pct": self.grip_pct,
            "temp_c": round(self.temp_c, 1),
        }


def calculate_tyre_wear_delta(
    compound: TyreCompound,
    pace_mode: str,
    track_temp_c: float,
    weather_state: str,
) -> float:
    """
    Computes percentage wear accrued during a single lap.
    Accounts for pace mode, thermal stress, and wet/dry mismatch (e.g. wet tyres burning up on dry track).
    """
    spec = COMPOUND_SPECS[compound]
    pace_multiplier = {
        "PUSH": 1.45,
        "NORMAL": 1.00,
        "CONSERVE": 0.70,
    }.get(pace_mode, 1.0)

    # Thermal delta penalty
    temp_diff = abs(track_temp_c - spec.optimal_temp_c)
    temp_factor = 1.0 + (temp_diff * spec.temp_sensitivity)

    # Overheating grooved tyres on dry track
    mismatch_wear = 1.0
    if weather_state == "DRY":
        if compound == TyreCompound.INTERMEDIATE:
            mismatch_wear = 2.2
        elif compound == TyreCompound.WET:
            mismatch_wear = 3.5

    wear_delta = spec.base_wear_rate_pct * pace_multiplier * temp_factor * mismatch_wear
    return wear_delta


def calculate_tyre_wear_penalty(tyre: TyreState) -> float:
    """
    Computes lap-time penalty (in seconds) incurred due to tyre wear.
    Uses a smooth linear degradation up to the cliff, then quadratic escalation beyond it.
    """
    spec = COMPOUND_SPECS[tyre.compound]
    wear = tyre.wear_pct

    if wear < spec.cliff_threshold_pct:
        # Linear degradation: e.g. 50% wear / 10 * 0.08 s = 0.40 s penalty
        return (wear / 10.0) * spec.linear_deg_s
    else:
        # Pre-cliff linear cost
        pre_cliff_loss = (spec.cliff_threshold_pct / 10.0) * spec.linear_deg_s
        # Non-linear post-cliff penalty
        cliff_delta = wear - spec.cliff_threshold_pct
        cliff_loss = (cliff_delta ** 2) * spec.cliff_deg_factor
        return pre_cliff_loss + cliff_loss


def calculate_weather_mismatch_penalty(compound: TyreCompound, weather_state: str) -> float:
    """
    Returns the lap-time penalty in seconds when tyres are mismatched with track conditions.
    """
    suitability = SUITABILITY.get((compound, weather_state), 0.5)
    if suitability >= 0.95:
        return 0.0
    # Inverse quadratic penalty for inappropriate tyre compounds
    # For slicks in heavy rain (suitability = 0.10): (1 - 0.10)^2 * 22.0 = 17.82 s loss!
    return ((1.0 - suitability) ** 2) * 22.0
