"""
Car state representation, dynamics, and telemetry properties.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

from engine.tyres import TyreState, TyreCompound
from engine.fuel import FuelState


@dataclass
class CarState:
    id: str = "CAR_01"
    driver_name: str = "Strategist AI"
    progress: float = 0.0          # 0..1 on circuit centerline
    speed_kmh: float = 245.0
    fuel: FuelState = field(default_factory=lambda: FuelState(fuel_kg=65.0, capacity_kg=105.0))
    tyre: TyreState = field(default_factory=lambda: TyreState(compound=TyreCompound.MEDIUM))
    pace_mode: str = "NORMAL"      # PUSH | NORMAL | CONSERVE
    position: int = 1
    gap_ahead_s: float = 0.0
    gap_behind_s: float = 1.8
    last_lap_time: float = 0.0
    best_lap_time: float = 999.0
    total_time: float = 0.0
    dnf: bool = False
    in_pit: bool = False

    def to_dict(self, burn_rate_per_lap: float) -> Dict[str, Any]:
        return {
            "progress": round(self.progress, 4),
            "speed_kmh": round(self.speed_kmh, 1),
            "fuel_kg": round(self.fuel.fuel_kg, 2),
            "fuel_capacity_kg": self.fuel.capacity_kg,
            "fuel_per_lap": round(burn_rate_per_lap, 2),
            "fuel_laps_remaining": self.fuel.laps_remaining(burn_rate_per_lap),
            "tyre": self.tyre.to_dict(),
            "pace_mode": self.pace_mode,
            "position": self.position,
            "gap_ahead_s": round(self.gap_ahead_s, 2),
            "gap_behind_s": round(self.gap_behind_s, 2),
            "last_lap_time": round(self.last_lap_time, 2),
            "best_lap_time": round(self.best_lap_time, 2) if self.best_lap_time < 900.0 else 0.0,
            "total_time": round(self.total_time, 2),
        }
