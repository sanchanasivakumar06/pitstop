"""
Strategy Registry and Factory.
"""

from typing import Dict, Type, List, Any

from engine.strategies.base import BaseStrategy, Decision
from engine.strategies.baseline_fixed import BaselineFixedStrategy
from engine.strategies.reactive_rules import ReactiveRulesStrategy
from engine.strategies.utility_agent import UtilityAgentStrategy
from engine.strategies.mdp_agent import MDPAgentStrategy
from engine.strategies.mdp_rollout import MDPRolloutStrategy

STRATEGY_REGISTRY: Dict[str, Type[BaseStrategy]] = {
    "baseline_fixed": BaselineFixedStrategy,
    "reactive_rules": ReactiveRulesStrategy,
    "utility_agent": UtilityAgentStrategy,
    "mdp_agent": MDPAgentStrategy,
    "mdp_mc_rollout": MDPRolloutStrategy,
}


def get_strategy(strategy_id: str) -> BaseStrategy:
    """Instantiates a strategy by its registered identifier."""
    cls = STRATEGY_REGISTRY.get(strategy_id, MDPAgentStrategy)
    return cls()


def list_strategies() -> List[Dict[str, Any]]:
    """Returns metadata for all available strategy algorithms."""
    results = []
    for sid, cls in STRATEGY_REGISTRY.items():
        instance = cls()
        results.append({
            "id": instance.name,
            "name": instance.name,
            "description": instance.description,
            "ai_concept": instance.ai_concept,
        })
    return results
