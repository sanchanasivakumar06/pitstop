"""
Belief state processing and discretization helpers for MDP integration.
"""

from __future__ import annotations
from typing import Dict, Tuple


def get_dominant_weather(belief: Dict[str, float]) -> str:
    """Returns the weather state with highest posterior probability."""
    return max(belief, key=belief.get)


def discretize_belief(belief: Dict[str, float]) -> int:
    """
    Maps continuous belief distribution into discrete MDP index.
    0: Dominant DRY
    1: Dominant LIGHT_RAIN
    2: Dominant HEAVY_RAIN
    """
    dom = get_dominant_weather(belief)
    mapping = {"DRY": 0, "LIGHT_RAIN": 1, "HEAVY_RAIN": 2}
    return mapping.get(dom, 0)


def belief_divergence(b1: Dict[str, float], b2: Dict[str, float]) -> float:
    """
    Computes Total Variation Distance (TVD) between two belief distributions.
    TVD = 0.5 * sum_i |p_i - q_i|
    Range: [0.0, 1.0]
    """
    all_keys = set(b1.keys()).union(b2.keys())
    l1_diff = sum(abs(b1.get(k, 0.0) - b2.get(k, 0.0)) for k in all_keys)
    return 0.5 * l1_diff
