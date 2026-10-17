"""
Fuel consumption model, tank capacity, weight penalty, and refuelling dynamics.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FuelConfig:
    tank_capacity_kg: float = 105.0       # Maximum fuel tank capacity
    base_consumption_kg: float = 1.75     # Base consumption per lap under normal conditions
    weight_penalty_s_per_kg: float = 0.033 # Lap time penalty per kg of onboard fuel (0.033 s/kg)
    refuel_rate_kg_s: float = 2.80        # Flow rate in pit stop: 2.8 kg per second (0.357 s per kg)
    min_reserve_kg: float = 2.0           # Reserve fuel buffer before starvation risk


@dataclass
class FuelState:
    fuel_kg: float
    capacity_kg: float = 105.0
    last_consumption_kg: float = 1.75

    @property
    def percentage(self) -> float:
        return max(0.0, min(100.0, round((self.fuel_kg / self.capacity_kg) * 100.0, 1)))

    def laps_remaining(self, burn_rate_per_lap: float) -> float:
        if burn_rate_per_lap <= 0:
            return 999.0
        return max(0.0, round(self.fuel_kg / burn_rate_per_lap, 1))

    def to_dict(self, burn_rate_per_lap: float) -> Dict[str, Any]:
        return {
            "fuel_kg": round(self.fuel_kg, 2),
            "fuel_capacity_kg": self.capacity_kg,
            "fuel_per_lap": round(burn_rate_per_lap, 2),
            "fuel_laps_remaining": self.laps_remaining(burn_rate_per_lap),
        }


def calculate_fuel_consumption(
    base_consumption_kg: float,
    pace_mode: str,
    weather_state: str,
) -> float:
    """
    Computes fuel consumed during a single lap.
    PUSH burns ~20% more fuel, CONSERVE burns ~18% less.
    Rain slightly decreases consumption due to lower full-throttle time.
    """
    pace_factor = {
        "PUSH": 1.22,
        "NORMAL": 1.00,
        "CONSERVE": 0.82,
    }.get(pace_mode, 1.0)

    weather_factor = {
        "DRY": 1.00,
        "LIGHT_RAIN": 0.94,
        "HEAVY_RAIN": 0.88,
    }.get(weather_state, 1.0)

    return base_consumption_kg * pace_factor * weather_factor


def calculate_fuel_weight_penalty(fuel_kg: float, penalty_per_kg: float = 0.033) -> float:
    """
    Returns the time lost per lap (in seconds) due to carrying fuel mass.
    E.g., 60 kg of fuel * 0.033 s/kg = 1.98 s/lap penalty.
    """
    return max(0.0, fuel_kg * penalty_per_kg)


def calculate_refuel_time(amount_kg: float, flow_rate_kg_s: float = 2.80) -> float:
    """
    Returns time in seconds required to pump the specified mass of fuel.
    """
    if amount_kg <= 0:
        return 0.0
    return amount_kg / flow_rate_kg_s
