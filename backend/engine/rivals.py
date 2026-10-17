"""
Rival AI cars simulation.
Provides 3 to 5 competitor cars with deterministic strategies for position, gaps, and traffic interaction.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any

from engine.tyres import TyreCompound, TyreState, calculate_tyre_wear_delta, calculate_tyre_wear_penalty, calculate_weather_mismatch_penalty
from engine.fuel import FuelState, calculate_fuel_consumption, calculate_fuel_weight_penalty
from engine.pit_stop import calculate_pit_stop_duration


@dataclass
class RivalCar:
    id: str
    name: str
    color: str
    progress: float = 0.0
    position: int = 2
    fuel: FuelState = field(default_factory=lambda: FuelState(fuel_kg=60.0))
    tyre: TyreState = field(default_factory=lambda: TyreState(compound=TyreCompound.MEDIUM))
    total_time: float = 0.0
    stops_done: int = 0
    planned_pit_laps: List[int] = field(default_factory=list)
    next_compound: TyreCompound = TyreCompound.HARD
    dnf: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "progress": round(self.progress, 4),
            "position": self.position,
            "tyre": self.tyre.compound.value,
            "color": self.color,
        }


def create_default_rivals(total_laps: int) -> List[RivalCar]:
    """Generates 4 distinct competitor cars with varied fixed pit lap cadences."""
    stop_mid = total_laps // 2
    stop_early = max(10, total_laps // 3)
    stop_late = min(total_laps - 8, (total_laps * 2) // 3)

    return [
        RivalCar(
            id="RIV_01",
            name="Scuderia Red",
            color="#ef4444",
            planned_pit_laps=[stop_mid],
            tyre=TyreState(compound=TyreCompound.SOFT),
            next_compound=TyreCompound.MEDIUM,
            fuel=FuelState(fuel_kg=70.0),
        ),
        RivalCar(
            id="RIV_02",
            name="Silver Arrow",
            color="#06b6d4",
            planned_pit_laps=[stop_late],
            tyre=TyreState(compound=TyreCompound.HARD),
            next_compound=TyreCompound.MEDIUM,
            fuel=FuelState(fuel_kg=75.0),
        ),
        RivalCar(
            id="RIV_03",
            name="Apex Racing",
            color="#f59e0b",
            planned_pit_laps=[stop_early, stop_late],
            tyre=TyreState(compound=TyreCompound.SOFT),
            next_compound=TyreCompound.SOFT,
            fuel=FuelState(fuel_kg=55.0),
        ),
        RivalCar(
            id="RIV_04",
            name="Phantom Bull",
            color="#8b5cf6",
            planned_pit_laps=[stop_mid],
            tyre=TyreState(compound=TyreCompound.MEDIUM),
            next_compound=TyreCompound.HARD,
            fuel=FuelState(fuel_kg=65.0),
        ),
    ]


def simulate_rival_lap(
    rival: RivalCar,
    lap: int,
    base_lap_s: float,
    weather_state: str,
    track_temp_c: float,
    base_pit_loss_s: float,
    sc_discount_s: float,
    rng: random.Random,
) -> float:
    """Simulates one lap for a rival car and increments its total race time."""
    if rival.dnf:
        return 999.0

    did_pit = False
    pit_time = 0.0

    # Reactive pit stop for rain if on slicks
    slicks = [TyreCompound.SOFT, TyreCompound.MEDIUM, TyreCompound.HARD]
    should_pit_for_rain = (weather_state in ["LIGHT_RAIN", "HEAVY_RAIN"] and rival.tyre.compound in slicks)
    scheduled_stop = lap in rival.planned_pit_laps

    if scheduled_stop or should_pit_for_rain:
        did_pit = True
        rival.stops_done += 1
        new_comp = TyreCompound.INTERMEDIATE if weather_state == "LIGHT_RAIN" else (
            TyreCompound.WET if weather_state == "HEAVY_RAIN" else rival.next_compound
        )
        pit_res = calculate_pit_stop_duration(
            base_pit_lane_loss_s=base_pit_loss_s,
            new_compound=new_comp.value,
            refuel_amount_kg=35.0,
            sc_discount_s=sc_discount_s,
            rng=rng,
        )
        pit_time = pit_res.total_pit_time_s
        rival.tyre = TyreState(compound=new_comp)
        rival.fuel.fuel_kg = min(rival.fuel.capacity_kg, rival.fuel.fuel_kg + 35.0)

    # Lap time calculation
    wear_delta = calculate_tyre_wear_delta(rival.tyre.compound, "NORMAL", track_temp_c, weather_state)
    rival.tyre.wear_pct = min(100.0, rival.tyre.wear_pct + wear_delta)
    rival.tyre.age_laps += 1

    wear_pen = calculate_tyre_wear_penalty(rival.tyre)
    fuel_pen = calculate_fuel_weight_penalty(rival.fuel.fuel_kg)
    weather_pen = calculate_weather_mismatch_penalty(rival.tyre.compound, weather_state)
    noise = rng.gauss(0.0, 0.15)

    lap_time = base_lap_s + rival.tyre.compound.value.count("H") * 0.4 + wear_pen + fuel_pen + weather_pen + noise + pit_time
    rival.total_time += lap_time

    # Burn fuel
    burn = calculate_fuel_consumption(1.75, "NORMAL", weather_state)
    rival.fuel.fuel_kg -= burn
    if rival.fuel.fuel_kg <= 0:
        rival.dnf = True
        rival.fuel.fuel_kg = 0.0

    return lap_time
