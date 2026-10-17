"""
Reactive Rule-Based Strategy.
Reacts to current threshold conditions: pits if tyre wear > 70%, rain is detected, or puncture occurs.
Does not perform forward optimization or backward induction.
"""

from __future__ import annotations
from typing import Dict, Any

from engine.agent.percepts import Percepts, Action
from engine.strategies.base import BaseStrategy, Decision
from engine.tyres import TyreCompound
from engine.explain import explain_decision


class ReactiveRulesStrategy(BaseStrategy):
    """Rule-based heuristic strategy using static IF-THEN threshold conditions."""

    def __init__(self):
        super().__init__(
            name="reactive_rules",
            description="Reactive heuristic rules (pits if tyre wear > 70% or rain detected)",
            ai_concept="Rule-Based Expert System (Heuristic / Reactive Without Lookahead)",
        )

    def reset(self, total_laps: int, track_id: str, scenario_name: str) -> None:
        pass

    def decide(self, percepts: Percepts) -> Decision:
        dom_weather = percepts.dominant_weather
        slicks = [TyreCompound.SOFT, TyreCompound.MEDIUM, TyreCompound.HARD]

        action = Action.STAY_OUT
        reason = "All telemetry metrics within standard operating thresholds"
        refuel = 0.0

        # Heuristic rules in priority order
        if percepts.has_puncture:
            action = Action.PIT_MEDIUM
            reason = "RULE TRIGGER: Emergency pit due to active puncture"
            refuel = 35.0
        elif dom_weather == "HEAVY_RAIN" and percepts.tyre_compound != TyreCompound.WET:
            action = Action.PIT_WET
            reason = "RULE TRIGGER: Heavy rain detected; pitting for Full Wets"
            refuel = 30.0
        elif dom_weather == "LIGHT_RAIN" and percepts.tyre_compound in slicks:
            action = Action.PIT_INTER
            reason = "RULE TRIGGER: Light rain detected; pitting for Intermediates"
            refuel = 30.0
        elif dom_weather == "DRY" and percepts.tyre_compound in [TyreCompound.INTERMEDIATE, TyreCompound.WET]:
            action = Action.PIT_MEDIUM
            reason = "RULE TRIGGER: Track dried up; pitting to remove grooved tyres"
            refuel = 30.0
        elif percepts.tyre_wear_pct >= 70.0:
            action = Action.PIT_MEDIUM
            reason = f"RULE TRIGGER: Tyre wear threshold exceeded ({percepts.tyre_wear_pct:.1f}% >= 70.0%)"
            refuel = 35.0
        elif percepts.fuel_kg < 5.0 and percepts.remaining_laps > 2:
            action = Action.PIT_MEDIUM
            reason = f"RULE TRIGGER: Fuel critical threshold reached ({percepts.fuel_kg:.1f} kg < 5.0 kg)"
            refuel = 40.0

        # Build mock Q-values / utilities reflecting rule priorities
        utilities = {
            act.value: (50.0 if act == action else -50.0)
            for act in [Action.STAY_OUT, Action.PIT_SOFT, Action.PIT_MEDIUM, Action.PIT_HARD, Action.PIT_INTER, Action.PIT_WET]
        }
        q_vals = {
            act.value: (3900.0 if act == action else 4100.0)
            for act in [Action.STAY_OUT, Action.PIT_SOFT, Action.PIT_MEDIUM, Action.PIT_HARD, Action.PIT_INTER, Action.PIT_WET]
        }

        explanation = [
            explain_decision(
                chosen_action=action.value,
                reason=reason,
                action_values=q_vals,
                value_type="Rule Priority Condition",
            )
        ]

        return Decision(
            action=action.value,
            reason=reason,
            pace_mode="NORMAL",
            refuel_amount_kg=refuel,
            utilities=utilities,
            q_values=q_vals,
            replanned=False,
            explanation=explanation,
        )
