"""
Dynamic stochastic race events: Safety Car, VSC, Punctures, and Engine Penalties.
Probabilistic event generation with seeded reproducibility.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class EventType(str, Enum):
    SAFETY_CAR = "SAFETY_CAR"
    VIRTUAL_SAFETY_CAR = "VIRTUAL_SAFETY_CAR"
    PUNCTURE = "PUNCTURE"
    ENGINE_PENALTY = "ENGINE_PENALTY"


@dataclass
class EventConfig:
    sc_base_prob: float = 0.025
    vsc_base_prob: float = 0.035
    puncture_base_prob: float = 0.004
    puncture_cliff_multiplier: float = 12.0  # Sharp increase when tyre is past cliff
    engine_penalty_prob: float = 0.015


class EventManager:
    """
    Tracks and triggers random seeded race events.
    """

    def __init__(
        self,
        config: EventConfig | None = None,
        scenario_name: str = "dry_race",
        rng: random.Random | None = None,
    ):
        self.config = config or EventConfig()
        self.scenario_name = scenario_name
        self.rng = rng or random.Random(42)

        # Tune probabilities based on scenario
        if scenario_name == "safety_car_heavy":
            self.config.sc_base_prob = 0.080
            self.config.vsc_base_prob = 0.060
        elif scenario_name == "wet_race":
            self.config.sc_base_prob = 0.050
            self.config.puncture_base_prob = 0.008

        self.sc_laps_remaining: int = 0
        self.vsc_laps_remaining: int = 0
        self.engine_penalty_laps_remaining: int = 0
        self.puncture_active: bool = False
        self.recent_events: List[str] = []

    @property
    def is_safety_car_active(self) -> bool:
        return self.sc_laps_remaining > 0

    @property
    def is_vsc_active(self) -> bool:
        return self.vsc_laps_remaining > 0

    def step_lap(self, tyre_past_cliff: bool) -> List[str]:
        """
        Advances active events and checks for new event occurrences.
        Returns a list of event tags triggered this lap.
        """
        triggered: List[str] = []
        self.puncture_active = False  # Reset per-lap puncture trigger

        # Decrement ongoing events
        if self.sc_laps_remaining > 0:
            self.sc_laps_remaining -= 1
            if self.sc_laps_remaining == 0:
                triggered.append("safety_car:end")

        if self.vsc_laps_remaining > 0:
            self.vsc_laps_remaining -= 1
            if self.vsc_laps_remaining == 0:
                triggered.append("vsc:end")

        if self.engine_penalty_laps_remaining > 0:
            self.engine_penalty_laps_remaining -= 1

        # Check for new safety car (only if no active SC)
        if self.sc_laps_remaining == 0 and self.vsc_laps_remaining == 0:
            r_sc = self.rng.random()
            if r_sc < self.config.sc_base_prob:
                self.sc_laps_remaining = self.rng.randint(2, 4)
                triggered.append("safety_car:start")
            else:
                r_vsc = self.rng.random()
                if r_vsc < self.config.vsc_base_prob:
                    self.vsc_laps_remaining = self.rng.randint(1, 2)
                    triggered.append("vsc:start")

        # Check for puncture (heavily dependent on tyre condition)
        puncture_p = self.config.puncture_base_prob
        if tyre_past_cliff:
            puncture_p *= self.config.puncture_cliff_multiplier

        if self.rng.random() < puncture_p:
            self.puncture_active = True
            triggered.append("puncture")

        # Engine penalty check
        if self.engine_penalty_laps_remaining == 0:
            if self.rng.random() < self.config.engine_penalty_prob:
                self.engine_penalty_laps_remaining = 2
                triggered.append("engine_penalty")

        self.recent_events = triggered
        return triggered

    def get_pit_stop_discount(self) -> float:
        """
        Under Safety Car or VSC, the pack is circulating slowly (delta pace),
        meaning a pit stop costs significantly less relative to cars on track!
        Returns time saved (in seconds).
        """
        if self.is_safety_car_active:
            # Huge pit window advantage: saves ~9-11 seconds relative to green flag stop
            return 10.5
        elif self.is_vsc_active:
            # Saves ~5-7 seconds
            return 6.0
        return 0.0

    def get_pace_delta_s(self) -> float:
        """
        Additional lap time enforced by SC, VSC, or engine penalty.
        """
        penalty = 0.0
        if self.is_safety_car_active:
            penalty += 32.0  # Slow neutralization pace
        elif self.is_vsc_active:
            penalty += 18.0
        if self.engine_penalty_laps_remaining > 0:
            penalty += 3.5
        if self.puncture_active:
            penalty += 26.0  # Limping back to the pits on a flat tyre
        return penalty
