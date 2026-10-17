"""
Tests for multi-race batch evaluation and paired comparison against baseline.
"""

import pytest
from engine.batch import run_batch_evaluation


def test_batch_evaluation_paired_comparison():
    """AI strategy (MDP) must outperform the fixed baseline across dynamic changing conditions."""
    results = run_batch_evaluation(
        strategies=["mdp_agent", "baseline_fixed"],
        scenarios=["changing_weather", "wet_race"],
        n_races=6,
        total_laps=25,
    )

    summary_map = {row["strategy"]: row for row in results["summary"]}
    mdp_summary = summary_map["mdp_agent"]
    baseline_summary = summary_map["baseline_fixed"]

    # In changing weather / wet races, MDP adapts tyres dynamically while baseline blindly sticks to slicks
    assert mdp_summary["mean"] <= baseline_summary["mean"]
    assert mdp_summary["win_rate"] >= 50.0
