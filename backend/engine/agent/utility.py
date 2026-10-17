"""
Utility Theory & Maximum Expected Utility (MEU) decision making.
U(action) = - (Expected remaining race time + risk penalties).
Decomposes utilities into explicit named terms for complete transparency.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

from engine.agent.percepts import Percepts, Action
from engine.tyres import (
    TyreCompound,
    COMPOUND_SPECS,
    calculate_tyre_wear_penalty,
    calculate_weather_mismatch_penalty,
)
from engine.pit_stop import calculate_pit_stop_duration


@dataclass
class UtilityTerms:
    pit_time_loss: float            # Immediate cost of taking pit stop (seconds)
    tyre_pace_gain: float           # Expected pace improvement from fresher rubber over remaining stint
    fuel_weight_gain: float         # Penalty change from refuelling mass vs burning fuel
    wear_risk_penalty: float        # Puncture / cliff cliff hazard penalty
    traffic_penalty: float          # Traffic re-entry impediment
    weather_mismatch_penalty: float # Expected mismatch based on Bayesian belief distribution
    net_utility: float              # Total utility score (higher = better, i.e. less negative time)

    def to_dict(self) -> Dict[str, float]:
        return {
            "pit_time_loss": round(self.pit_time_loss, 2),
            "tyre_pace_gain": round(self.tyre_pace_gain, 2),
            "fuel_weight_gain": round(self.fuel_weight_gain, 2),
            "wear_risk_penalty": round(self.wear_risk_penalty, 2),
            "traffic_penalty": round(self.traffic_penalty, 2),
            "weather_mismatch_penalty": round(self.weather_mismatch_penalty, 2),
            "net_utility": round(self.net_utility, 2),
        }


def compute_expected_weather_mismatch(compound: TyreCompound, weather_belief: Dict[str, float]) -> float:
    """Computes expected weather mismatch penalty under belief distribution."""
    return sum(
        prob * calculate_weather_mismatch_penalty(compound, weather_state)
        for weather_state, prob in weather_belief.items()
    )


def evaluate_action_utility(
    action: Action,
    percepts: Percepts,
    base_lap_s: float = 88.5,
    base_pit_lane_loss_s: float = 22.5,
) -> UtilityTerms:
    """
    Evaluates utility U(action) for a given candidate action.
    U(a) = - [ (pit_time_loss) - (tyre_pace_gain) + (fuel_weight_gain) + (wear_risk) + (traffic) + (weather_mismatch) ]
    """
    remaining_laps = max(1, percepts.remaining_laps)
    # Estimate average laps this choice will govern (up to remaining laps, capped at typical stint length)
    stint_horizon = min(remaining_laps, 18)

    # 1. Pit time loss
    sc_discount = 10.5 if percepts.is_safety_car else (6.0 if percepts.is_vsc else 0.0)

    if action == Action.STAY_OUT:
        pit_time_loss = 0.0
        active_compound = percepts.tyre_compound
        fresh_tyres = False
    else:
        # Mapping pit action to compound
        compound_map = {
            Action.PIT_SOFT: TyreCompound.SOFT,
            Action.PIT_MEDIUM: TyreCompound.MEDIUM,
            Action.PIT_HARD: TyreCompound.HARD,
            Action.PIT_INTER: TyreCompound.INTERMEDIATE,
            Action.PIT_WET: TyreCompound.WET,
        }
        active_compound = compound_map[action]
        fresh_tyres = True

        # Calculate needed refuel: if remaining laps require more fuel than current
        needed_fuel = remaining_laps * 1.75
        refuel_amount = max(0.0, min(105.0 - percepts.fuel_kg, needed_fuel - percepts.fuel_kg + 3.0))

        pit_breakdown = calculate_pit_stop_duration(
            base_pit_lane_loss_s=base_pit_lane_loss_s,
            new_compound=active_compound.value,
            refuel_amount_kg=refuel_amount,
            allow_refuelling=True,
            sc_discount_s=sc_discount,
        )
        pit_time_loss = pit_breakdown.net_time_loss_s

    # 2. Tyre pace gain (benefit of fresh compound vs current worn tyres)
    current_wear_pen = calculate_tyre_wear_penalty(
        type("TempTyre", (), {"compound": percepts.tyre_compound, "wear_pct": percepts.tyre_wear_pct})()
    )

    if fresh_tyres:
        # Fresh tyre starts with 0 wear and optimal grip
        target_spec = COMPOUND_SPECS[active_compound]
        current_spec = COMPOUND_SPECS[percepts.tyre_compound]
        compound_delta = target_spec.base_pace_delta_s - current_spec.base_pace_delta_s
        # Total pace gain across stint
        tyre_pace_gain = (current_wear_pen - compound_delta) * stint_horizon
    else:
        tyre_pace_gain = 0.0

    # 3. Fuel weight gain
    fuel_weight_gain = 0.0
    if not fresh_tyres:
        # Fuel starvation catastrophe penalty if staying out with insufficient fuel
        fuel_needed = remaining_laps * 1.75
        if percepts.fuel_kg < min(5.0, fuel_needed * 0.5):
            fuel_weight_gain = 9999.0  # Avoid DNF

    # 4. Wear risk penalty (cliff or puncture)
    wear_risk = 0.0
    if action == Action.STAY_OUT:
        spec = COMPOUND_SPECS[percepts.tyre_compound]
        if percepts.tyre_wear_pct >= spec.cliff_threshold_pct:
            # Harsh exponential risk penalty for running past the cliff
            wear_risk = (percepts.tyre_wear_pct - spec.cliff_threshold_pct + 1.0) * 12.0
        if percepts.has_puncture:
            wear_risk += 5000.0  # Must box for puncture!
    else:
        wear_risk = 0.0

    # 5. Traffic penalty
    traffic = 0.0
    if action != Action.STAY_OUT:
        # If behind a car within 1.0s, pitting might give undercut/clean air!
        if percepts.gap_ahead_s < 1.0:
            traffic = -2.5  # Benefit of free air undercut
        else:
            traffic = 1.0

    # 6. Expected weather mismatch penalty
    expected_mismatch_per_lap = compute_expected_weather_mismatch(active_compound, percepts.weather_belief)
    weather_mismatch_penalty = expected_mismatch_per_lap * stint_horizon

    # Net utility = - (Total expected time cost)
    # Higher utility (less negative) is preferred
    total_time_cost = (
        pit_time_loss
        - tyre_pace_gain
        + fuel_weight_gain
        + wear_risk
        + traffic
        + weather_mismatch_penalty
    )
    net_utility = -total_time_cost

    return UtilityTerms(
        pit_time_loss=pit_time_loss,
        tyre_pace_gain=tyre_pace_gain,
        fuel_weight_gain=fuel_weight_gain,
        wear_risk_penalty=wear_risk,
        traffic_penalty=traffic,
        weather_mismatch_penalty=weather_mismatch_penalty,
        net_utility=net_utility,
    )


def select_best_action_utility(
    percepts: Percepts,
    base_lap_s: float = 88.5,
    base_pit_lane_loss_s: float = 22.5,
) -> Tuple[Action, str, Dict[str, float], Dict[str, UtilityTerms]]:
    """
    Calculates Maximum Expected Utility (MEU) across all actions.
    Returns (best_action, reason, utilities_dict, terms_dict).
    """
    candidate_actions = [
        Action.STAY_OUT,
        Action.PIT_SOFT,
        Action.PIT_MEDIUM,
        Action.PIT_HARD,
        Action.PIT_INTER,
        Action.PIT_WET,
    ]

    utilities: Dict[str, float] = {}
    terms: Dict[str, UtilityTerms] = {}

    for action in candidate_actions:
        term = evaluate_action_utility(action, percepts, base_lap_s, base_pit_lane_loss_s)
        terms[action.value] = term
        utilities[action.value] = term.net_utility

    best_action_str = max(utilities, key=utilities.get)
    best_action = Action(best_action_str)

    # Formulate rational explanation
    if percepts.has_puncture and best_action != Action.STAY_OUT:
        reason = "Emergency pit stop forced by tyre puncture"
    elif percepts.is_safety_car and best_action != Action.STAY_OUT:
        reason = f"Exploited Safety Car window for cheap stop onto {best_action_str.replace('PIT_', '')}"
    elif best_action != Action.STAY_OUT:
        best_term = terms[best_action_str]
        reason = (
            f"Expected tyre pace gain ({best_term.tyre_pace_gain:.1f}s) outweighs pit loss ({best_term.pit_time_loss:.1f}s) "
            f"under {percepts.dominant_weather} weather belief"
        )
    else:
        reason = f"Current {percepts.tyre_compound.value} tyres optimal; remaining pace outweighs pit overhead"

    return best_action, reason, utilities, terms
