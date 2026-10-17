"""
Per-race and multi-race evaluation metrics calculation.
Computes race completion time, win-rate against baseline, consistency scores, and statistical spreads.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class RaceMetrics:
    total_race_time: float = 0.0
    final_position: int = 1
    pit_stops: int = 0
    pit_time_total: float = 0.0
    avg_lap_time: float = 0.0
    fuel_used: float = 0.0
    fuel_left_at_finish: float = 0.0
    tyre_wear_at_pits: List[float] = field(default_factory=list)
    replans: int = 0
    events_count: int = 0
    time_lost_to_wrong_tyres: float = 0.0
    dnf: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_time": round(self.total_race_time, 2),
            "final_position": self.final_position,
            "pit_stops": self.pit_stops,
            "pit_time_total": round(self.pit_time_total, 2),
            "avg_lap_time": round(self.avg_lap_time, 2),
            "fuel_used": round(self.fuel_used, 2),
            "fuel_left_at_finish": round(self.fuel_left_at_finish, 2),
            "tyre_wear_at_pits": [round(w, 1) for w in self.tyre_wear_at_pits],
            "replans": self.replans,
            "events_count": self.events_count,
            "time_lost_to_wrong_tyres": round(self.time_lost_to_wrong_tyres, 2),
            "dnf": self.dnf,
        }


@dataclass
class BatchMetrics:
    strategy_name: str
    runs_count: int
    mean_time: float
    std_time: float
    min_time: float
    max_time: float
    avg_pit_stops: float
    avg_replans: float
    win_rate_vs_baseline_pct: float
    time_saved_vs_baseline_s: float
    consistency_score_pct: float   # 100 - (CV * 100)
    dnf_count: int
    scenario_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy_name,
            "runs": self.runs_count,
            "mean": round(self.mean_time, 2),
            "std": round(self.std_time, 2),
            "min": round(self.min_time, 2),
            "max": round(self.max_time, 2),
            "avg_pit_stops": round(self.avg_pit_stops, 2),
            "avg_replans": round(self.avg_replans, 1),
            "win_rate": round(self.win_rate_vs_baseline_pct, 1),
            "time_saved": round(self.time_saved_vs_baseline_s, 2),
            "consistency": round(self.consistency_score_pct, 1),
            "dnfs": self.dnf_count,
            "scenarios": self.scenario_breakdown,
        }


def compute_batch_statistics(
    strategy_name: str,
    race_results: List[RaceMetrics],
    baseline_results: List[RaceMetrics] | None = None,
    scenario_tags: List[str] | None = None,
) -> BatchMetrics:
    """Computes aggregate statistical metrics over multiple seeded simulation runs."""
    times = [r.total_race_time for r in race_results if not r.dnf]
    n = len(race_results)
    dnfs = sum(1 for r in race_results if r.dnf)

    if not times:
        return BatchMetrics(
            strategy_name=strategy_name,
            runs_count=n,
            mean_time=99999.0,
            std_time=0.0,
            min_time=99999.0,
            max_time=99999.0,
            avg_pit_stops=0.0,
            avg_replans=0.0,
            win_rate_vs_baseline_pct=0.0,
            time_saved_vs_baseline_s=0.0,
            consistency_score_pct=0.0,
            dnf_count=dnfs,
        )

    mean_t = sum(times) / len(times)
    var_t = sum((t - mean_t) ** 2 for t in times) / (len(times) if len(times) > 1 else 1)
    std_t = math.sqrt(var_t)
    min_t = min(times)
    max_t = max(times)
    avg_stops = sum(r.pit_stops for r in race_results) / n
    avg_replans = sum(r.replans for r in race_results) / n

    # Consistency score: based on coefficient of variation (CV = std / mean)
    cv = (std_t / mean_t) if mean_t > 0 else 1.0
    consistency_pct = max(0.0, min(100.0, round((1.0 - (cv * 5.0)) * 100.0, 1)))

    # Win rate and delta time against baseline (paired seeds)
    win_rate = 0.0
    time_saved = 0.0
    if baseline_results and len(baseline_results) == n:
        wins = 0
        deltas = []
        for agent_res, base_res in zip(race_results, baseline_results):
            if agent_res.dnf and not base_res.dnf:
                continue
            if not agent_res.dnf and base_res.dnf:
                wins += 1
                deltas.append(500.0)
            elif not agent_res.dnf and not base_res.dnf:
                delta = base_res.total_race_time - agent_res.total_race_time
                deltas.append(delta)
                if delta > 0.0:
                    wins += 1
        win_rate = (wins / n) * 100.0
        time_saved = (sum(deltas) / len(deltas)) if deltas else 0.0

    # Per-scenario breakdown
    breakdown: Dict[str, Dict[str, float]] = {}
    if scenario_tags and len(scenario_tags) == n:
        unique_scenarios = set(scenario_tags)
        for sc in unique_scenarios:
            sc_times = [r.total_race_time for r, tag in zip(race_results, scenario_tags) if tag == sc and not r.dnf]
            if sc_times:
                breakdown[sc] = {
                    "mean": round(sum(sc_times) / len(sc_times), 2),
                    "min": round(min(sc_times), 2),
                    "max": round(max(sc_times), 2),
                }

    return BatchMetrics(
        strategy_name=strategy_name,
        runs_count=n,
        mean_time=round(mean_t, 2),
        std_time=round(std_t, 2),
        min_time=round(min_t, 2),
        max_time=round(max_t, 2),
        avg_pit_stops=round(avg_stops, 2),
        avg_replans=round(avg_replans, 1),
        win_rate_vs_baseline_pct=round(win_rate, 1),
        time_saved_vs_baseline_s=round(time_saved, 2),
        consistency_score_pct=round(consistency_pct, 1),
        dnf_count=dnfs,
        scenario_breakdown=breakdown,
    )
