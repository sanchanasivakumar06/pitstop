"""
Data export service supporting JSON and CSV formats for race analysis.
"""

from __future__ import annotations
import csv
import io
import json
from typing import List, Dict, Any, Tuple


def export_race_data(snapshots: List[Dict[str, Any]], export_format: str = "json") -> Tuple[str, str]:
    """
    Exports simulation snapshots to JSON or CSV string.
    Returns (content_string, media_type).
    """
    if export_format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header row
        writer.writerow([
            "lap",
            "sim_time_s",
            "phase",
            "position",
            "speed_kmh",
            "fuel_kg",
            "fuel_per_lap",
            "tyre_compound",
            "tyre_age_laps",
            "tyre_wear_pct",
            "tyre_grip_pct",
            "weather_state",
            "weather_dry_belief",
            "weather_light_belief",
            "weather_heavy_belief",
            "action_chosen",
            "action_reason",
            "pit_in_progress",
            "last_lap_time",
            "total_time",
        ])

        for s in snapshots:
            car = s.get("car", {})
            tyre = car.get("tyre", {})
            weather = s.get("weather", {})
            belief = weather.get("belief", {})
            decision = s.get("decision", {})
            pit = s.get("pit", {})

            writer.writerow([
                s.get("lap", 0),
                s.get("sim_time", 0.0),
                s.get("phase", ""),
                car.get("position", 1),
                car.get("speed_kmh", 0.0),
                car.get("fuel_kg", 0.0),
                car.get("fuel_per_lap", 0.0),
                tyre.get("compound", ""),
                tyre.get("age_laps", 0),
                tyre.get("wear_pct", 0.0),
                tyre.get("grip_pct", 0.0),
                weather.get("true_state", ""),
                belief.get("DRY", 0.0),
                belief.get("LIGHT_RAIN", 0.0),
                belief.get("HEAVY_RAIN", 0.0),
                decision.get("action", ""),
                decision.get("reason", ""),
                pit.get("in_progress", False),
                car.get("last_lap_time", 0.0),
                car.get("total_time", 0.0),
            ])

        return output.getvalue(), "text/csv"

    # Default to JSON
    return json.dumps(snapshots, indent=2), "application/json"
