"""
Baseline Strategy: Fixed Lap Pit Stop Strategy.
Pre-determines pit stops at fixed lap intervals (e.g. Lap N/2) and uses identical compounds,
completely blind to changing weather, tyre wear, or Safety Car windows.
"""

from __future__ import annotations
from typing import List, Dict, Any

from engine.agent.percepts import Percepts, Action
from engine.strategies.base import BaseStrategy, Decision
from engine.explain import explain_decision


class BaselineFixedStrategy(BaseStrategy):
    """Pits at pre-scheduled fixed lap numbers regardless of race events."""

    def __init__(self):
        super().__init__(
            name="baseline_fixed",
            description="Fixed pit lap strategy (pits at N/2, ignores weather & tyre wear)",
            ai_concept="Deterministic Fixed Baseline (No AI / Zero Adaptation)",
        )
        self.planned_laps: List[int] = []

    def reset(self, total_laps: int, track_id: str, scenario_name: str) -> None:
        if total_laps > 70:
            # 2-stop schedule for endurance
            self.planned_laps = [total_laps // 3, (2 * total_laps) // 3]
        else:
            # 1-stop schedule at half distance
            self.planned_laps = [total_laps // 2]

    def decide(self, percepts: Percepts) -> Decision:
        should_pit = percepts.lap in self.planned_laps
        action_name = "PIT_MEDIUM" if should_pit else "STAY_OUT"

        if should_pit:
            reason = f"Pre-scheduled fixed pit stop at lap {percepts.lap} (ignores weather/wear)"
        else:
            reason = f"Circulating on track according to fixed plan; next pit at lap {self.planned_laps[-1]}"

        # Fixed baseline has static pseudo-utilities for UI display
        utilities = {
            "STAY_OUT": 0.0 if not should_pit else -100.0,
            "PIT_MEDIUM": 0.0 if should_pit else -100.0,
            "PIT_SOFT": -20.0,
            "PIT_HARD": -20.0,
            "PIT_INTER": -50.0,
            "PIT_WET": -80.0,
        }
        q_vals = {
            "STAY_OUT": 4000.0 if not should_pit else 4500.0,
            "PIT_MEDIUM": 4000.0 if should_pit else 4500.0,
            "PIT_SOFT": 4100.0,
            "PIT_HARD": 4150.0,
            "PIT_INTER": 4300.0,
            "PIT_WET": 4600.0,
        }

        explanation = [
            explain_decision(
                chosen_action=action_name,
                reason=reason,
                action_values=q_vals,
                value_type="Fixed Schedule",
            )
        ]

        refuel_amount = 35.0 if should_pit else 0.0

        return Decision(
            action=action_name,
            reason=reason,
            pace_mode="NORMAL",
            refuel_amount_kg=refuel_amount,
            utilities=utilities,
            q_values=q_vals,
            replanned=False,
            explanation=explanation,
        )
