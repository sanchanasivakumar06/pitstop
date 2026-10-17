"""
Flagship Strategy: Markov Decision Process (MDP) with Dynamic Replanning.
Computes globally optimal pit stop and compound policies via backward induction over laps.
Continuously monitors for environmental distribution shifts and triggers rapid replanning (<50ms).
"""

from __future__ import annotations
from typing import Dict, Any, Optional

from engine.agent.percepts import Percepts, Action
from engine.agent.mdp import MDPSolver
from engine.agent.belief import get_dominant_weather, belief_divergence
from engine.strategies.base import BaseStrategy, Decision
from engine.explain import explain_decision
from engine.track import get_track


class MDPAgentStrategy(BaseStrategy):
    """Flagship AI agent: Finite-horizon MDP backward induction with belief-shift replanning."""

    def __init__(self):
        super().__init__(
            name="mdp_agent",
            description="Markov Decision Process (MDP) with Dynamic Programming Backward Induction & Event Replanning",
            ai_concept="Markov Decision Process (MDP) + Dynamic Programming + Bayesian Replanning",
        )
        self.solver: Optional[MDPSolver] = None
        self.total_laps: int = 60
        self.track_id: str = "silverstone_classic"
        self.scenario_name: str = "changing_weather"
        self.replan_count: int = 0
        self.last_belief: Dict[str, float] = {}
        self.last_sc_state: bool = False
        self.last_puncture_state: bool = False

    def reset(self, total_laps: int, track_id: str, scenario_name: str) -> None:
        self.total_laps = total_laps
        self.track_id = track_id
        self.scenario_name = scenario_name
        self.replan_count = 0
        track = get_track(track_id)

        self.solver = MDPSolver(
            total_laps=total_laps,
            base_lap_s=track.base_lap_time_s,
            base_pit_loss_s=track.pit_lane_loss_s,
            scenario_name=scenario_name,
        )
        self.solver.solve(start_lap=0)
        self.last_belief = {"DRY": 1.0, "LIGHT_RAIN": 0.0, "HEAVY_RAIN": 0.0}
        self.last_sc_state = False
        self.last_puncture_state = False

    def decide(self, percepts: Percepts) -> Decision:
        if self.solver is None:
            self.reset(percepts.total_laps, self.track_id, self.scenario_name)

        # Detect conditions requiring dynamic re-planning
        did_replan = False
        belief_shift = belief_divergence(percepts.weather_belief, self.last_belief) if self.last_belief else 0.0
        sc_toggled = percepts.is_safety_car != self.last_sc_state
        puncture_event = percepts.has_puncture and not self.last_puncture_state

        if belief_shift > 0.35 or sc_toggled or puncture_event:
            # Re-solve backward induction from current lap onwards
            self.solver.solve(start_lap=percepts.lap)
            self.replan_count += 1
            did_replan = True

        self.last_belief = dict(percepts.weather_belief)
        self.last_sc_state = percepts.is_safety_car
        self.last_puncture_state = percepts.has_puncture

        # Get exact Q-values (expected total remaining time in seconds)
        q_values = self.solver.get_action_q_values(percepts)

        # Action with lowest expected remaining time is optimal!
        best_action_str = min(q_values, key=q_values.get)
        best_action = Action(best_action_str)
        best_q = q_values[best_action_str]

        # Determine rationale
        stay_out_q = q_values.get("STAY_OUT", best_q)
        time_saved = stay_out_q - best_q

        if percepts.has_puncture and best_action != Action.STAY_OUT:
            reason = f"Emergency replan: puncture detected. Pitting for fresh rubber saves {time_saved:.1f} s."
        elif percepts.is_safety_car and best_action != Action.STAY_OUT:
            reason = f"Safety Car deployed: discounted pit stop window exploited. Saves {time_saved:.1f} s vs staying out."
        elif best_action != Action.STAY_OUT:
            reason = f"Optimal DP policy: Q({best_action_str})={best_q:.1f} s vs Q(STAY_OUT)={stay_out_q:.1f} s -> pit saves {time_saved:.1f} s."
        else:
            reason = f"Optimal DP policy: Staying out maintains minimum expected remaining time ({best_q:.1f} s)."

        # Refuelling quantity
        refuel = 0.0
        if best_action != Action.STAY_OUT:
            needed = percepts.remaining_laps * 1.75
            refuel = max(0.0, min(105.0 - percepts.fuel_kg, needed - percepts.fuel_kg + 3.0))

        # Pace mode
        if percepts.tyre_wear_pct < 45.0 and percepts.gap_ahead_s < 1.2 and not percepts.is_safety_car:
            pace_mode = "PUSH"
        elif percepts.tyre_wear_pct > 68.0 or percepts.fuel_kg < 7.0:
            pace_mode = "CONSERVE"
        else:
            pace_mode = "NORMAL"

        # Utilities representation: U = -Q (normalized for UI comparison bar chart)
        min_q = min(q_values.values())
        utilities = {
            act: round(-(val - min_q), 2)
            for act, val in q_values.items()
        }

        explanation = [
            explain_decision(
                chosen_action=best_action_str,
                reason=reason,
                action_values=q_values,
                value_type="MDP Q-Value (Expected Total Remaining Time in Seconds)",
            )
        ]

        return Decision(
            action=best_action_str,
            reason=reason,
            pace_mode=pace_mode,
            refuel_amount_kg=refuel,
            utilities=utilities,
            q_values=q_values,
            replanned=did_replan,
            explanation=explanation,
        )
