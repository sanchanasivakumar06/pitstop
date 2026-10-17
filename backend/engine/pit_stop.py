"""
Pit-stop execution, duration calculation, and staged animation phases.
Phases: ENTRY -> BOX_STOP -> TYRE_CHANGE -> REFUEL -> EXIT.
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

from engine.fuel import calculate_refuel_time


class PitStage(str, Enum):
    NONE = "NONE"
    ENTRY = "ENTRY"
    BOX_STOP = "BOX_STOP"
    TYRE_CHANGE = "TYRE_CHANGE"
    REFUEL = "REFUEL"
    EXIT = "EXIT"


@dataclass
class PitStopBreakdown:
    total_pit_time_s: float
    pit_lane_loss_s: float
    tyre_change_time_s: float
    refuel_time_s: float
    crew_variance_s: float
    sc_discount_s: float
    net_time_loss_s: float
    refuel_amount_kg: float
    new_compound: str

    def to_explanation(self) -> Dict[str, Any]:
        return {
            "id": "pit_stop_time",
            "title": "Pit Stop Time Calculation",
            "formula": "T_pit = (T_pitlane - Discount_SC) + T_stationary + Crew_variance",
            "inputs": {
                "pit_lane_loss_s": round(self.pit_lane_loss_s, 2),
                "safety_car_discount_s": round(self.sc_discount_s, 2),
                "tyre_change_time_s": round(self.tyre_change_time_s, 2),
                "refuel_time_s": round(self.refuel_time_s, 2),
                "crew_variance_s": round(self.crew_variance_s, 2),
            },
            "steps": [
                f"1. Pit lane speed limit transit: {self.pit_lane_loss_s:.2f} s",
                f"2. Safety car timing discount: -{self.sc_discount_s:.2f} s",
                f"3. Stationary tyre swap: {self.tyre_change_time_s:.2f} s",
                f"4. Refuelling ({self.refuel_amount_kg:.1f} kg): {self.refuel_time_s:.2f} s",
                f"5. Crew execution variance: {self.crew_variance_s:+.2f} s",
                f"6. Net stationary stop duration: {max(self.tyre_change_time_s, self.refuel_time_s) + self.crew_variance_s:.2f} s",
            ],
            "result": f"Total pit loss: {self.net_time_loss_s:.2f} s (stationary: {self.tyre_change_time_s + self.crew_variance_s:.2f} s)",
            "plain_english": f"The stop required {self.total_pit_time_s:.2f}s total (net race loss {self.net_time_loss_s:.2f}s) fitting {self.new_compound} tyres.",
        }


def calculate_pit_stop_duration(
    base_pit_lane_loss_s: float,
    new_compound: str,
    refuel_amount_kg: float = 0.0,
    allow_refuelling: bool = True,
    sc_discount_s: float = 0.0,
    rng: random.Random | None = None,
) -> PitStopBreakdown:
    """
    Computes total pit stop duration including transit and stationary servicing.
    """
    base_tyre_change = 2.45  # Elite F1/WEC pit crew tyre change benchmark

    refuel_time = 0.0
    if allow_refuelling and refuel_amount_kg > 0:
        refuel_time = calculate_refuel_time(refuel_amount_kg, flow_rate_kg_s=2.80)

    crew_variance = 0.0
    if rng:
        crew_variance = rng.gauss(0.0, 0.25)
        # Small chance of a minor wheel nut fumble (+1.5s)
        if rng.random() < 0.05:
            crew_variance += rng.uniform(1.2, 2.2)

    # In modern regulations with parallel refuel or tyre-only:
    # If refuel is allowed, either parallel (max) or sequential (sum)
    stationary_service = max(base_tyre_change, refuel_time) if allow_refuelling else base_tyre_change
    stationary_total = max(2.0, stationary_service + crew_variance)

    net_transit = max(6.0, base_pit_lane_loss_s - sc_discount_s)
    total_time = net_transit + stationary_total

    return PitStopBreakdown(
        total_pit_time_s=round(total_time, 2),
        pit_lane_loss_s=base_pit_lane_loss_s,
        tyre_change_time_s=base_tyre_change,
        refuel_time_s=round(refuel_time, 2),
        crew_variance_s=round(crew_variance, 2),
        sc_discount_s=sc_discount_s,
        net_time_loss_s=round(total_time, 2),
        refuel_amount_kg=refuel_amount_kg,
        new_compound=new_compound,
    )
