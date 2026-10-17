"""
Main Race Simulation Loop.
Executes lap-by-lap simulation, coordinates car dynamics, rivals, stochastic weather,
seeded random events, AI strategy execution, and produces conformant JSON snapshots.
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional

from engine.track import TrackConfig, get_track
from engine.tyres import (
    TyreCompound,
    TyreState,
    calculate_tyre_wear_delta,
    calculate_weather_mismatch_penalty,
)
from engine.fuel import (
    FuelState,
    FuelConfig,
    calculate_fuel_consumption,
)
from engine.weather import WeatherModel
from engine.events import EventManager
from engine.lap_time import calculate_lap_time, LapTimeBreakdown
from engine.pit_stop import calculate_pit_stop_duration, PitStage, PitStopBreakdown
from engine.car import CarState
from engine.rivals import RivalCar, create_default_rivals, simulate_rival_lap
from engine.agent.percepts import Percepts, Action
from engine.strategies.base import BaseStrategy, Decision
from engine.strategies import get_strategy
from engine.metrics import RaceMetrics
from engine.explain import explain_fuel, explain_tyre_wear


@dataclass
class RaceSimulationConfig:
    seed: int = 42
    track_id: str = "silverstone_classic"
    total_laps: int = 60
    strategy_id: str = "mdp_agent"
    scenario_name: str = "changing_weather"
    start_fuel_kg: float = 65.0
    start_tyre_compound: TyreCompound = TyreCompound.MEDIUM
    allow_refuelling: bool = True


class RaceSimulation:
    """
    Complete deterministic race simulation.
    Uses partitioned seeded RNG streams for weather, dynamic events, and lap execution noise.
    """

    def __init__(self, config: RaceSimulationConfig | None = None):
        self.config = config or RaceSimulationConfig()
        self.track: TrackConfig = get_track(self.config.track_id)
        self.total_laps: int = self.config.total_laps

        # Deterministic master RNG and partitioned sub-streams
        self.master_rng = random.Random(self.config.seed)
        self.weather_rng = random.Random(self.master_rng.randint(0, 1000000))
        self.event_rng = random.Random(self.master_rng.randint(0, 1000000))
        self.lap_rng = random.Random(self.master_rng.randint(0, 1000000))
        self.rival_rng = random.Random(self.master_rng.randint(0, 1000000))

        # Core simulation subsystems
        self.weather_model = WeatherModel(
            scenario_name=self.config.scenario_name,
            initial_state="LIGHT_RAIN" if self.config.scenario_name == "wet_race" else "DRY",
            rng=self.weather_rng,
        )
        self.event_manager = EventManager(
            scenario_name=self.config.scenario_name,
            rng=self.event_rng,
        )
        self.car = CarState(
            fuel=FuelState(fuel_kg=self.config.start_fuel_kg, capacity_kg=105.0),
            tyre=TyreState(compound=self.config.start_tyre_compound),
        )
        self.rivals: List[RivalCar] = create_default_rivals(self.total_laps)
        self.strategy: BaseStrategy = get_strategy(self.config.strategy_id)
        self.strategy.reset(self.total_laps, self.track.id, self.config.scenario_name)

        # State counters
        self.current_lap: int = 0
        self.sim_time_s: float = 0.0
        self.is_finished: bool = False
        self.pit_stops_count: int = 0
        self.pit_time_accumulated: float = 0.0
        self.replans_count: int = 0
        self.tyre_wears_at_pit: List[float] = []
        self.time_lost_to_mismatch: float = 0.0
        self.total_fuel_consumed: float = 0.0
        self.recent_events_log: List[str] = []

        # Current lap snapshot buffer
        self.latest_decision: Optional[Decision] = None
        self.latest_pit_breakdown: Optional[PitStopBreakdown] = None
        self.planned_next_pit_lap: Optional[int] = None

    def _build_percepts(self) -> Percepts:
        return Percepts(
            lap=self.current_lap,
            total_laps=self.total_laps,
            fuel_kg=self.car.fuel.fuel_kg,
            tyre_compound=self.car.tyre.compound,
            tyre_wear_pct=self.car.tyre.wear_pct,
            tyre_age_laps=self.car.tyre.age_laps,
            track_temp_c=self.weather_model.track_temp_c,
            gap_ahead_s=self.car.gap_ahead_s,
            gap_behind_s=self.car.gap_behind_s,
            weather_belief=dict(self.weather_model.belief),
            is_safety_car=self.event_manager.is_safety_car_active,
            is_vsc=self.event_manager.is_vsc_active,
            has_puncture=self.event_manager.puncture_active,
        )

    def step_lap(self) -> Dict[str, Any]:
        """
        Executes a single race lap and returns the full JSON snapshot.
        """
        if self.is_finished:
            return self.get_snapshot()

        self.current_lap += 1
        events_this_lap: List[str] = []

        # 1. Weather step and observation
        old_weather = self.weather_model.current_state
        new_weather, obs = self.weather_model.step_environment()
        if new_weather != old_weather:
            events_this_lap.append(f"weather_change:{new_weather}")

        # Bayesian forward belief update
        updated_belief, weather_explanation = self.weather_model.bayesian_filter_update(obs)

        # 2. Race events step
        event_tags = self.event_manager.step_lap(tyre_past_cliff=self.car.tyre.is_past_cliff)
        events_this_lap.extend(event_tags)

        # 3. AI Agent decision cycle
        percepts = self._build_percepts()
        decision = self.strategy.decide(percepts)
        self.latest_decision = decision
        self.car.pace_mode = decision.pace_mode

        if decision.replanned:
            self.replans_count += 1
            events_this_lap.append("replan")

        # 4. Process pit stop action
        did_pit = decision.action != "STAY_OUT"
        pit_time_loss = 0.0
        sc_discount = self.event_manager.get_pit_stop_discount()

        if did_pit:
            self.pit_stops_count += 1
            self.tyre_wears_at_pit.append(self.car.tyre.wear_pct)
            events_this_lap.append("pit:start")

            # Extract target compound
            compound_map = {
                "SOFT": TyreCompound.SOFT,
                "MEDIUM": TyreCompound.MEDIUM,
                "HARD": TyreCompound.HARD,
                "INTER": TyreCompound.INTERMEDIATE,
                "INTERMEDIATE": TyreCompound.INTERMEDIATE,
                "WET": TyreCompound.WET,
            }
            target_str = decision.action.replace("PIT_", "")
            target_compound = compound_map.get(target_str, TyreCompound.MEDIUM)

            pit_breakdown = calculate_pit_stop_duration(
                base_pit_lane_loss_s=self.track.pit_lane_loss_s,
                new_compound=target_compound.value,
                refuel_amount_kg=decision.refuel_amount_kg,
                allow_refuelling=self.config.allow_refuelling,
                sc_discount_s=sc_discount,
                rng=self.lap_rng,
            )
            self.latest_pit_breakdown = pit_breakdown
            pit_time_loss = pit_breakdown.net_time_loss_s
            self.pit_time_accumulated += pit_time_loss

            # Apply pit service
            self.car.tyre = TyreState(compound=target_compound)
            if self.config.allow_refuelling and decision.refuel_amount_kg > 0:
                self.car.fuel.fuel_kg = min(
                    self.car.fuel.capacity_kg,
                    self.car.fuel.fuel_kg + decision.refuel_amount_kg,
                )
            events_this_lap.append("pit:end")

        # 5. Lap dynamics and lap time calculation
        prev_wear = self.car.tyre.wear_pct
        wear_delta = calculate_tyre_wear_delta(
            self.car.tyre.compound,
            self.car.pace_mode,
            self.weather_model.track_temp_c,
            new_weather,
        )
        self.car.tyre.wear_pct = min(100.0, self.car.tyre.wear_pct + wear_delta)
        self.car.tyre.age_laps += 1

        prev_fuel = self.car.fuel.fuel_kg
        burn = calculate_fuel_consumption(
            1.75,
            self.car.pace_mode,
            new_weather,
        )
        self.car.fuel.fuel_kg = max(0.0, self.car.fuel.fuel_kg - burn)
        self.car.fuel.last_consumption_kg = burn
        self.total_fuel_consumed += burn

        if self.car.fuel.fuel_kg <= 0.0:
            self.car.dnf = True
            events_this_lap.append("fuel_starvation:DNF")
        elif self.car.fuel.fuel_kg < 5.0:
            events_this_lap.append("fuel_low")

        # Calculate exact lap time
        event_pace_delta = self.event_manager.get_pace_delta_s()
        lap_breakdown = calculate_lap_time(
            base_lap_s=self.track.base_lap_time_s,
            tyre=self.car.tyre,
            fuel_kg=self.car.fuel.fuel_kg,
            weather_state=new_weather,
            pace_mode=self.car.pace_mode,
            gap_ahead_s=self.car.gap_ahead_s,
            event_delta_s=event_pace_delta,
            rng=self.lap_rng,
        )

        total_lap_duration = lap_breakdown.total_lap_time_s + pit_time_loss
        self.car.last_lap_time = total_lap_duration
        self.car.total_time += total_lap_duration
        if total_lap_duration < self.car.best_lap_time and not did_pit:
            self.car.best_lap_time = total_lap_duration

        self.sim_time_s += total_lap_duration
        self.time_lost_to_mismatch += lap_breakdown.weather_penalty_s

        # 6. Simulate rival cars
        for rival in self.rivals:
            simulate_rival_lap(
                rival=rival,
                lap=self.current_lap,
                base_lap_s=self.track.base_lap_time_s,
                weather_state=new_weather,
                track_temp_c=self.weather_model.track_temp_c,
                base_pit_loss_s=self.track.pit_lane_loss_s,
                sc_discount_s=sc_discount,
                rng=self.rival_rng,
            )

        # 7. Update race ranking and gaps
        all_competitors = [(self.car.id, self.car.total_time, self.car)] + [
            (riv.id, riv.total_time, riv) for riv in self.rivals
        ]
        # Sort by total race time
        all_competitors.sort(key=lambda x: x[1])
        positions = {entry[0]: rank + 1 for rank, entry in enumerate(all_competitors)}
        self.car.position = positions[self.car.id]
        for riv in self.rivals:
            riv.position = positions[riv.id]

        # Calculate gaps
        car_idx = [e[0] for e in all_competitors].index(self.car.id)
        if car_idx > 0:
            self.car.gap_ahead_s = round(self.car.total_time - all_competitors[car_idx - 1][1], 2)
        else:
            self.car.gap_ahead_s = 0.0

        if car_idx < len(all_competitors) - 1:
            self.car.gap_behind_s = round(all_competitors[car_idx + 1][1] - self.car.total_time, 2)
        else:
            self.car.gap_behind_s = 99.0

        # Check race finish
        if self.current_lap >= self.total_laps or self.car.dnf:
            self.is_finished = True
            events_this_lap.append("race_finished")

        # 8. Assemble explanation blocks for all UI 'i' info buttons
        fuel_expl = explain_fuel(
            prev_fuel_kg=prev_fuel,
            burned_kg=burn,
            remaining_fuel_kg=self.car.fuel.fuel_kg,
            burn_rate_per_lap=burn,
            pace_mode=self.car.pace_mode,
            weather_state=new_weather,
        )
        spec = self.car.tyre.compound
        from engine.tyres import COMPOUND_SPECS
        tyre_expl = explain_tyre_wear(
            compound=spec.value,
            prev_wear_pct=prev_wear,
            wear_delta_pct=wear_delta,
            new_wear_pct=self.car.tyre.wear_pct,
            cliff_threshold_pct=COMPOUND_SPECS[spec].cliff_threshold_pct,
            grip_pct=self.car.tyre.grip_pct,
            pace_mode=self.car.pace_mode,
        )
        lap_expl = lap_breakdown.to_explanation()

        # Combine all explanation entries into the decision
        all_explanations = list(decision.explanation)
        all_explanations.extend([lap_expl, fuel_expl, tyre_expl, weather_explanation])
        if self.latest_pit_breakdown:
            all_explanations.append(self.latest_pit_breakdown.to_explanation())

        decision.explanation = all_explanations
        self.recent_events_log = events_this_lap

        return self.get_snapshot(did_pit=did_pit)

    def get_snapshot(self, did_pit: bool = False, sub_lap_progress: float = 1.0) -> Dict[str, Any]:
        """Formats the current state into the standard snapshot JSON schema."""
        phase = "RACING"
        if self.is_finished:
            phase = "FINISHED"
        elif self.event_manager.is_safety_car_active:
            phase = "SAFETY_CAR"
        elif did_pit:
            phase = "PIT_BOX"

        pit_stage = "NONE"
        pit_progress = 0.0
        if did_pit:
            pit_stage = "TYRE_CHANGE"
            pit_progress = 0.50

        burn_rate = self.car.fuel.last_consumption_kg or 1.75
        avg_lap = (self.car.total_time / self.current_lap) if self.current_lap > 0 else 0.0

        return {
            "lap": self.current_lap,
            "total_laps": self.total_laps,
            "sim_time": round(self.sim_time_s, 2),
            "phase": phase,
            "car": self.car.to_dict(burn_rate),
            "rivals": [r.to_dict() for r in self.rivals],
            "weather": self.weather_model.to_dict(),
            "pit": {
                "in_progress": did_pit,
                "stage": pit_stage,
                "stage_progress": pit_progress,
                "planned_next_pit_lap": self.planned_next_pit_lap,
                "stops_done": self.pit_stops_count,
                "time_loss_s": round(self.pit_time_accumulated, 2),
            },
            "decision": self.latest_decision.to_dict() if self.latest_decision else {
                "action": "STAY_OUT",
                "reason": "Initial race formation lap",
                "utilities": {},
                "q_values": {},
                "replanned": False,
                "explanation": [],
            },
            "events": self.recent_events_log,
            "metrics": {
                "total_time": round(self.car.total_time, 2),
                "pit_stops": self.pit_stops_count,
                "replans": self.replans_count,
                "fuel_used": round(self.total_fuel_consumed, 2),
                "avg_lap_time": round(avg_lap, 2),
            },
        }

    def run_full_race(self) -> Tuple[List[Dict[str, Any]], RaceMetrics]:
        """Executes the race completely and returns all lap snapshots and final metrics."""
        snapshots: List[Dict[str, Any]] = []
        while not self.is_finished:
            snap = self.step_lap()
            snapshots.append(snap)

        metrics = RaceMetrics(
            total_race_time=self.car.total_time,
            final_position=self.car.position,
            pit_stops=self.pit_stops_count,
            pit_time_total=self.pit_time_accumulated,
            avg_lap_time=(self.car.total_time / self.total_laps) if self.total_laps > 0 else 0.0,
            fuel_used=self.total_fuel_consumed,
            fuel_left_at_finish=self.car.fuel.fuel_kg,
            tyre_wear_at_pits=self.tyre_wears_at_pit,
            replans=self.replans_count,
            events_count=len(self.event_manager.recent_events),
            time_lost_to_wrong_tyres=self.time_lost_to_mismatch,
            dnf=self.car.dnf,
        )

        return snapshots, metrics
