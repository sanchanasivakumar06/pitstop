"""
Intelligent Agent Percepts, Action Space, and PEAS Framework.

PEAS Specification:
------------------
1. Performance Measure:
   - Primary: Minimize total race completion time (sum of lap times + pit stops).
   - Secondary: Avoid DNF (fuel starvation, catastrophic puncture), maximize finishing position.
2. Environment:
   - Stochastic, dynamic, partially observable, sequential, continuous-state / discrete-time.
   - Dynamic track temperature, Markov weather changes, random Safety Car / VSC deployments.
3. Actuators:
   - Strategic Pit Decisions: STAY_OUT, PIT_SOFT, PIT_MEDIUM, PIT_HARD, PIT_INTER, PIT_WET.
   - Refuel Mass (kg to take on during stop).
   - Tactical Pace Mode: PUSH, NORMAL, CONSERVE.
4. Sensors:
   - Telemetry: Lap counter, fuel remaining (kg), tyre compound, tyre age (laps), tyre wear (%).
   - Environmental: Track temperature (°C), rain sensor, noisy track grip estimate.
   - Competitors: Gaps ahead/behind (s), relative track position.
   - Race Control Flags: Green flag, Safety Car (SC), Virtual Safety Car (VSC).
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

from engine.tyres import TyreCompound


class Action(str, Enum):
    STAY_OUT = "STAY_OUT"
    PIT_SOFT = "PIT_SOFT"
    PIT_MEDIUM = "PIT_MEDIUM"
    PIT_HARD = "PIT_HARD"
    PIT_INTER = "PIT_INTER"
    PIT_WET = "PIT_WET"


class PaceMode(str, Enum):
    PUSH = "PUSH"
    NORMAL = "NORMAL"
    CONSERVE = "CONSERVE"


@dataclass
class Percepts:
    """Current sensor percept snapshot received by the rational agent."""
    lap: int
    total_laps: int
    fuel_kg: float
    tyre_compound: TyreCompound
    tyre_wear_pct: float
    tyre_age_laps: int
    track_temp_c: float
    gap_ahead_s: float
    gap_behind_s: float
    weather_belief: Dict[str, float]  # Probability distribution: {"DRY": p1, "LIGHT_RAIN": p2, "HEAVY_RAIN": p3}
    is_safety_car: bool
    is_vsc: bool
    has_puncture: bool
    fuel_capacity_kg: float = 105.0

    @property
    def dominant_weather(self) -> str:
        return max(self.weather_belief, key=self.weather_belief.get)

    @property
    def remaining_laps(self) -> int:
        return max(0, self.total_laps - self.lap)
