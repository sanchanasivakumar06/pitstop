"""
Explainability engine for the Race Strategist AI.
Produces structured, LaTeX-free step-by-step mathematical explanations
for every core race metric and strategy decision to power the 'i' info buttons.
"""

from __future__ import annotations
from typing import Dict, List, Any


def explain_decision(
    chosen_action: str,
    reason: str,
    action_values: Dict[str, float],
    value_type: str = "Q-value (Remaining Race Time in Seconds)",
) -> Dict[str, Any]:
    """
    Builds the 'Why this decision?' explanation comparing the selected action against all alternatives.
    """
    sorted_actions = sorted(action_values.items(), key=lambda x: x[1])
    best_action, best_val = sorted_actions[0]
    runner_up_action, runner_up_val = sorted_actions[1] if len(sorted_actions) > 1 else (best_action, best_val)
    delta_s = abs(runner_up_val - best_val)

    steps = [
        f"1. Evaluated candidate actions using {value_type} optimization.",
    ]
    for action, val in sorted_actions:
        marker = " [CHOSEN]" if action == chosen_action else ""
        steps.append(f"   • {action}: {val:.2f} s{marker}")

    steps.append(f"2. Delta advantage over runner-up ({runner_up_action}): {delta_s:.2f} seconds.")

    return {
        "id": "strategy_decision",
        "title": "Strategy Decision Rationality (MEU / MDP)",
        "formula": "a* = argmin_{a in A} Q(s, a)  [or argmax Utility U(a)]",
        "inputs": {action: round(val, 2) for action, val in action_values.items()},
        "steps": steps,
        "result": f"Selected {chosen_action} (Saving {delta_s:.2f} s vs {runner_up_action})",
        "plain_english": f"The AI picked {chosen_action} because {reason}. This decision saves {delta_s:.2f} seconds across the remaining laps.",
    }


def explain_fuel(
    prev_fuel_kg: float,
    burned_kg: float,
    remaining_fuel_kg: float,
    burn_rate_per_lap: float,
    pace_mode: str,
    weather_state: str,
) -> Dict[str, Any]:
    """Builds explanation for fuel consumption and remaining laps."""
    laps_left = round(remaining_fuel_kg / burn_rate_per_lap, 1) if burn_rate_per_lap > 0 else 0.0
    return {
        "id": "fuel_calculation",
        "title": "Fuel Consumption & Stint Range",
        "formula": "Fuel_new = Fuel_prev - (Base_rate * Pace_factor * Weather_factor)",
        "inputs": {
            "prev_fuel_kg": round(prev_fuel_kg, 2),
            "burned_this_lap_kg": round(burned_kg, 2),
            "pace_mode": pace_mode,
            "weather_state": weather_state,
        },
        "steps": [
            f"1. Previous onboard fuel: {prev_fuel_kg:.2f} kg",
            f"2. Burn rate adjustment: {pace_mode} mode and {weather_state} track",
            f"3. Fuel consumed during lap: -{burned_kg:.2f} kg",
            f"4. Resulting usable fuel: {remaining_fuel_kg:.2f} kg",
            f"5. Projected range at current pace: {laps_left} laps",
        ],
        "result": f"{remaining_fuel_kg:.2f} kg remaining ({laps_left} laps of fuel)",
        "plain_english": f"Burning {burned_kg:.2f} kg this lap leaves {remaining_fuel_kg:.2f} kg onboard, giving a range of approximately {laps_left} laps.",
    }


def explain_tyre_wear(
    compound: str,
    prev_wear_pct: float,
    wear_delta_pct: float,
    new_wear_pct: float,
    cliff_threshold_pct: float,
    grip_pct: float,
    pace_mode: str,
) -> Dict[str, Any]:
    """Builds explanation for tyre degradation and cliff distance."""
    past_cliff = new_wear_pct >= cliff_threshold_pct
    cliff_margin = max(0.0, cliff_threshold_pct - new_wear_pct)
    status_str = "PAST CLIFF (Severe degradation active!)" if past_cliff else f"{cliff_margin:.1f}% buffer before cliff"

    return {
        "id": "tyre_wear_calculation",
        "title": "Tyre Wear & Thermal Degradation",
        "formula": "Wear_new = Wear_prev + (Base_wear * Pace_mult * Temp_factor * Mismatch)",
        "inputs": {
            "compound": compound,
            "prev_wear_pct": round(prev_wear_pct, 1),
            "wear_delta_pct": round(wear_delta_pct, 2),
            "cliff_threshold_pct": round(cliff_threshold_pct, 1),
            "pace_mode": pace_mode,
        },
        "steps": [
            f"1. Compound: {compound} (cliff threshold at {cliff_threshold_pct:.0f}% wear)",
            f"2. Previous wear: {prev_wear_pct:.1f}%",
            f"3. Wear added this lap in {pace_mode} mode: +{wear_delta_pct:.2f}%",
            f"4. Total accumulated wear: {new_wear_pct:.1f}%",
            f"5. Remaining mechanical grip: {grip_pct:.1f}%",
            f"6. Degradation zone: {status_str}",
        ],
        "result": f"{new_wear_pct:.1f}% wear ({grip_pct:.1f}% grip)",
        "plain_english": f"Accumulated {new_wear_pct:.1f}% wear on {compound} tyres with {grip_pct:.1f}% grip remaining. {status_str}.",
    }
