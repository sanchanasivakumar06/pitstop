"""
Request schemas for race creation and batch evaluation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RaceCreateRequest(BaseModel):
    seed: int = Field(default=42, description="Simulation RNG seed for determinism")
    track_id: str = Field(default="silverstone_classic", description="Track identifier")
    total_laps: int = Field(default=50, ge=5, le=300, description="Total race laps")
    strategy_id: str = Field(default="mdp_agent", description="Strategy algorithm identifier")
    scenario_name: str = Field(default="changing_weather", description="Scenario weather/hazard preset")
    start_fuel_kg: float = Field(default=65.0, ge=10.0, le=105.0, description="Starting fuel mass")
    start_tyre_compound: str = Field(default="MEDIUM", description="Starting tyre compound")
    allow_refuelling: bool = Field(default=True, description="Whether pit lane refuelling is permitted")


class EvaluationRequest(BaseModel):
    strategies: Optional[List[str]] = Field(default=None, description="Strategies to evaluate")
    scenarios: Optional[List[str]] = Field(default=None, description="Scenarios to evaluate")
    n_races: int = Field(default=10, ge=2, le=200, description="Number of paired seeded races")
    seeds: Optional[List[int]] = Field(default=None, description="Explicit seeds")
    track_id: str = Field(default="silverstone_classic", description="Track identifier")
    total_laps: int = Field(default=40, ge=5, le=150, description="Laps per race in evaluation")
