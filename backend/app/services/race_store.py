"""
In-memory Race Run Store.
Thread-safe storage for race configurations, active simulation instances, and generated snapshots.
Interface designed to be easily swappable with a persistent database.
"""

from __future__ import annotations
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class StoredRace:
    race_id: str
    config: Dict[str, Any]
    simulation: Any
    snapshots: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None
    status: str = "CREATED"  # CREATED | RUNNING | PAUSED | FINISHED
    created_at: float = field(default_factory=time.time)


class RaceStore:
    """In-memory key-value store for active and completed race runs."""

    def __init__(self):
        self._races: Dict[str, StoredRace] = {}

    def save_race(self, race: StoredRace) -> None:
        self._races[race.race_id] = race

    def get_race(self, race_id: str) -> Optional[StoredRace]:
        return self._races.get(race_id)

    def list_races(self) -> List[Dict[str, Any]]:
        return [
            {
                "race_id": r.race_id,
                "config": r.config,
                "status": r.status,
                "laps_done": len(r.snapshots),
                "total_laps": r.config.get("total_laps", 0),
                "created_at": r.created_at,
            }
            for r in self._races.values()
        ]

    def delete_race(self, race_id: str) -> bool:
        if race_id in self._races:
            del self._races[race_id]
            return True
        return False


# Singleton store instance
_global_race_store = RaceStore()


def get_race_store() -> RaceStore:
    return _global_race_store
