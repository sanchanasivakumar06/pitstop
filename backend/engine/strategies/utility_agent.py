"""
Expected Utility Maximizer Agent (Utility Theory + Bayesian Belief).
Evaluates actions by decomposing expected remaining race time into explicit utility terms:
pit_time_loss, tyre_pace_gain, fuel_weight_gain, wear_risk_penalty, traffic_penalty, weather_mismatch_penalty.
Selects action with Maximum Expected Utility (MEU).
"""

from __future__ import annotations
from typing import Dict, Any

from engine.agent.percepts import Percepts, Action
from engine.agent.utility import select_best_action_utility
from engine.strategies.base import BaseStrategy, Decision
from engine.explain import explain_decision
from engine.track import get_track


class UtilityAgentStrategy(BaseStrategy):
    """Rational agent using Utility Theory and Bayesian belief to maximize expected utility."""

    def __init__(self):
        super().__init__(
            name="utility_agent",
            description="One-step Expected Utility Maximizer (MEU with 6 decomposed utility terms & belief state)",
            ai_concept="Utility Theory & Probabilistic Reasoning (MEU + Bayesian HMM)",
        )
        self.base_lap_s = 88.5
        self.base_pit_loss_s = 22.5

    def reset(self, total_laps: int, track_id: str, scenario_name: str) -> None:
        track = get_track(track_id)
        self.base_lap_s = track.base_lap_time_s
        self.base_pit_loss_s = track.pit_lane_loss_s

    def decide(self, percepts: Percepts) -> Decision:
        best_action, reason, utilities, terms = select_best_action_utility(
            percepts,
            base_lap_s=self.base_lap_s,
            base_pit_lane_loss_s=self.base_pit_loss_s,
        )

        # Tactical pace mode decision
        if percepts.tyre_wear_pct < 40.0 and percepts.gap_ahead_s < 1.5 and not percepts.is_safety_car:
            pace_mode = "PUSH"
        elif percepts.tyre_wear_pct > 65.0 or (percepts.fuel_kg < 8.0 and percepts.remaining_laps > 4):
            pace_mode = "CONSERVE"
        else:
            pace_mode = "NORMAL"

        refuel = 0.0
        if best_action != Action.STAY_OUT:
            needed = percepts.remaining_laps * 1.75
            refuel = max(0.0, min(105.0 - percepts.fuel_kg, needed - percepts.fuel_kg + 4.0))

        # Build Q-value equivalent (approximate remaining time = -utility)
        # Shift baseline so Q is positive seconds
        baseline_remaining_time = percepts.remaining_laps * self.base_lap_s
        q_vals = {
            act: round(baseline_remaining_time - util, 2)
            for act, util in utilities.items()
        }

        # Build explanation block
        best_term = terms[best_action.value]
        term_explanation = {
            "id": "utility_breakdown",
            "title": f"Expected Utility Breakdown for {best_action.value}",
            "formula": "U(a) = - [ Pit_loss - Pace_gain + Fuel_gain + Wear_risk + Traffic + Mismatch ]",
            "inputs": best_term.to_dict(),
            "steps": [
                f"1. Pit stop time loss: {best_term.pit_time_loss:.2f} s",
                f"2. Projected tyre pace gain: -{best_term.tyre_pace_gain:.2f} s",
                f"3. Fuel mass delta penalty: +{best_term.fuel_weight_gain:.2f} s",
                f"4. Wear / cliff / puncture risk: +{best_term.wear_risk_penalty:.2f} s",
                f"5. Traffic interference: +{best_term.traffic_penalty:.2f} s",
                f"6. Bayesian weather mismatch risk: +{best_term.weather_mismatch_penalty:.2f} s",
            ],
            "result": f"Net Utility U = {best_term.net_utility:.2f} (Rank #1)",
            "plain_english": f"Action {best_action.value} achieves maximum expected utility ({best_term.net_utility:.2f}) across all 6 risk & pace factors.",
        }

        explanation = [
            explain_decision(
                chosen_action=best_action.value,
                reason=reason,
                action_values=q_vals,
                value_type="Expected Utility / Remaining Time",
            ),
            term_explanation,
        ]

        return Decision(
            action=best_action.value,
            reason=reason,
            pace_mode=pace_mode,
            refuel_amount_kg=refuel,
            utilities=utilities,
            q_values=q_vals,
            replanned=False,
            explanation=explanation,
        )
