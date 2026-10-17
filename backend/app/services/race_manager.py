"""
Race Manager Service.
Orchestrates race creation, stepping, full simulation, and state queries.
"""

from __future__ import annotations
import uuid
from typing import Dict, List, Optional, Any

from app.schemas.config import RaceCreateRequest
from app.services.race_store import RaceStore, StoredRace, get_race_store
from engine.race import RaceSimulation, RaceSimulationConfig
from engine.tyres import TyreCompound


class RaceManager:
    """Coordinates lifecycle and execution of race simulations."""

    def __init__(self, store: RaceStore | None = None):
        self.store = store or get_race_store()

    def create_race(self, req: RaceCreateRequest) -> str:
        race_id = f"race_{uuid.uuid4().hex[:8]}"

        target_compound = getattr(TyreCompound, req.start_tyre_compound, TyreCompound.MEDIUM)
        config = RaceSimulationConfig(
            seed=req.seed,
            track_id=req.track_id,
            total_laps=req.total_laps,
            strategy_id=req.strategy_id,
            scenario_name=req.scenario_name,
            start_fuel_kg=req.start_fuel_kg,
            start_tyre_compound=target_compound,
            allow_refuelling=req.allow_refuelling,
        )

        sim = RaceSimulation(config)
        stored = StoredRace(
            race_id=race_id,
            config=req.model_dump(),
            simulation=sim,
            status="CREATED",
        )
        self.store.save_race(stored)
        return race_id

    def get_race_info(self, race_id: str) -> Optional[Dict[str, Any]]:
        stored = self.store.get_race(race_id)
        if not stored:
            return None

        return {
            "race_id": stored.race_id,
            "status": stored.status,
            "config": stored.config,
            "laps_completed": len(stored.snapshots),
            "total_laps": stored.config.get("total_laps", 0),
            "metrics": stored.metrics,
            "latest_snapshot": stored.snapshots[-1] if stored.snapshots else None,
        }

    def get_snapshots(self, race_id: str) -> Optional[List[Dict[str, Any]]]:
        stored = self.store.get_race(race_id)
        if not stored:
            return None
        # If not finished, simulate to completion to return full list for offline export
        if stored.status != "FINISHED":
            self.run_full_race(race_id)
        return stored.snapshots

    def step_lap(self, race_id: str) -> Optional[Dict[str, Any]]:
        stored = self.store.get_race(race_id)
        if not stored:
            return None

        sim: RaceSimulation = stored.simulation
        if sim.is_finished:
            stored.status = "FINISHED"
            return stored.snapshots[-1] if stored.snapshots else sim.get_snapshot()

        stored.status = "RUNNING"
        snap = sim.step_lap()
        stored.snapshots.append(snap)

        if sim.is_finished:
            stored.status = "FINISHED"
            stored.metrics = {
                "total_time": sim.car.total_time,
                "pit_stops": sim.pit_stops_count,
                "final_position": sim.car.position,
                "fuel_left": sim.car.fuel.fuel_kg,
                "avg_lap_time": sim.car.total_time / sim.total_laps if sim.total_laps > 0 else 0.0,
                "dnf": sim.car.dnf,
            }

        return snap

    def run_full_race(self, race_id: str) -> Optional[Dict[str, Any]]:
        stored = self.store.get_race(race_id)
        if not stored:
            return None

        sim: RaceSimulation = stored.simulation
        if stored.status == "FINISHED":
            return stored.metrics

        while not sim.is_finished:
            snap = sim.step_lap()
            stored.snapshots.append(snap)

        stored.status = "FINISHED"
        metrics = {
            "total_time": round(sim.car.total_time, 2),
            "pit_stops": sim.pit_stops_count,
            "final_position": sim.car.position,
            "fuel_left": round(sim.car.fuel.fuel_kg, 2),
            "avg_lap_time": round(sim.car.total_time / sim.total_laps, 2) if sim.total_laps > 0 else 0.0,
            "dnf": sim.car.dnf,
        }
        stored.metrics = metrics
        return metrics


_global_race_manager = RaceManager()


def get_race_manager() -> RaceManager:
    return _global_race_manager
