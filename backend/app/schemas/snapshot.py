"""
Pydantic schema definitions for simulation snapshots, telemetry, decisions, and explanations.
Shared contract mirrored in TypeScript for the frontend client.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class TyreModel(BaseModel):
    compound: str
    age_laps: int
    wear_pct: float
    grip_pct: float
    temp_c: float


class CarModel(BaseModel):
    progress: float
    speed_kmh: float
    fuel_kg: float
    fuel_capacity_kg: float
    fuel_per_lap: float
    fuel_laps_remaining: float
    tyre: TyreModel
    pace_mode: str
    position: int
    gap_ahead_s: float
    gap_behind_s: float
    last_lap_time: float
    best_lap_time: float
    total_time: float


class RivalModel(BaseModel):
    id: str
    progress: float
    position: int
    tyre: str
    color: str


class WeatherModelSchema(BaseModel):
    true_state: str
    belief: Dict[str, float]
    track_temp_c: float
    grip: float


class PitModel(BaseModel):
    in_progress: bool
    stage: str
    stage_progress: float
    planned_next_pit_lap: Optional[int] = None
    stops_done: int
    time_loss_s: float


class ExplanationModel(BaseModel):
    id: str
    title: str
    formula: str
    inputs: Dict[str, Any]
    steps: List[str]
    result: str
    plain_english: str


class DecisionModel(BaseModel):
    action: str
    reason: str
    utilities: Dict[str, float] = Field(default_factory=dict)
    q_values: Dict[str, float] = Field(default_factory=dict)
    replanned: bool = False
    explanation: List[ExplanationModel] = Field(default_factory=list)


class MetricsModel(BaseModel):
    total_time: float
    pit_stops: int
    replans: int
    fuel_used: float
    avg_lap_time: float


class SnapshotModel(BaseModel):
    lap: int
    total_laps: int
    sim_time: float
    phase: str
    car: CarModel
    rivals: List[RivalModel]
    weather: WeatherModelSchema
    pit: PitModel
    decision: DecisionModel
    events: List[str] = Field(default_factory=list)
    metrics: MetricsModel
