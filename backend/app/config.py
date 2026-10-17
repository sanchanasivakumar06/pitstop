"""
Application global settings and default configurations.
"""

from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "The Impossible Pit Stop - Race Strategist API"
    version: str = "1.0.0"
    api_prefix: str = "/api"
    cors_origins: List[str] = ["*"]
    default_seed: int = 42
    default_track: str = "silverstone_classic"
    default_laps: int = 50
    default_strategy: str = "mdp_agent"
    default_scenario: str = "changing_weather"


settings = Settings()
