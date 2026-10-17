"""
REST endpoints for strategy algorithms, track presets, and scenario metadata.
"""

from typing import List, Dict, Any
from fastapi import APIRouter

from engine.strategies import list_strategies
from engine.track import TRACK_PRESETS
from engine.weather import TRANSITION_MATRICES

router = APIRouter()


SCENARIO_METADATA = [
    {
        "id": "dry_race",
        "name": "Dry Grand Prix",
        "description": "Consistent dry weather with 97% dry state persistence. Tests tire thermal conservation and optimal stint length.",
        "weather_volatility": "Low",
        "safety_car_risk": "Low (2.5%)",
    },
    {
        "id": "changing_weather",
        "name": "Dynamic Changing Weather",
        "description": "Highly volatile transitions between Dry, Light Rain, and Heavy Rain. Tests Bayesian belief updates and agile replanning.",
        "weather_volatility": "High (35% shift chance)",
        "safety_car_risk": "Moderate (4%)",
    },
    {
        "id": "wet_race",
        "name": "Monsoon Wet Race",
        "description": "Heavy standing water and frequent rain surges. Demands timely transition between Intermediates and Full Wets.",
        "weather_volatility": "Moderate",
        "safety_car_risk": "High (5%)",
    },
    {
        "id": "safety_car_heavy",
        "name": "Incident Packed (Safety Car Heavy)",
        "description": "Multiple incidents and Safety Car periods. Rewards agents that exploit discounted pit loss under caution windows.",
        "weather_volatility": "Moderate",
        "safety_car_risk": "Extreme (8%)",
    },
    {
        "id": "high_degradation",
        "name": "High Tyre Degradation",
        "description": "Rough track surface and high track temperature accelerating tyre wear cliff approach. Tests MEU wear risk aversion.",
        "weather_volatility": "Low",
        "safety_car_risk": "Low (2.5%)",
    },
]


@router.get("/strategies")
def get_strategies() -> List[Dict[str, Any]]:
    """Returns available AI decision strategies and their theoretical foundation."""
    return list_strategies()


@router.get("/scenarios")
def get_scenarios() -> List[Dict[str, Any]]:
    """Returns available scenario presets and hazard characteristics."""
    return SCENARIO_METADATA


@router.get("/tracks")
def get_tracks() -> List[Dict[str, Any]]:
    """Returns preset tracks complete with 2D spline control points and pit lane geometry."""
    return [track.to_dict() for track in TRACK_PRESETS.values()]
