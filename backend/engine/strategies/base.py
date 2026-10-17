"""
Strategy abstract interface and Decision payload structure.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any

from engine.agent.percepts import Percepts, Action, PaceMode


@dataclass
class Decision:
    action: str                       # e.g. "STAY_OUT", "PIT_MEDIUM"
    reason: str                       # Plain English rationale
    pace_mode: str = "NORMAL"         # "PUSH", "NORMAL", "CONSERVE"
    refuel_amount_kg: float = 0.0     # Recommended refuel mass if pitting
    utilities: Dict[str, float] = field(default_factory=dict)
    q_values: Dict[str, float] = field(default_factory=dict)
    replanned: bool = False
    explanation: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "reason": self.reason,
            "utilities": self.utilities,
            "q_values": self.q_values,
            "replanned": self.replanned,
            "explanation": self.explanation,
        }


class BaseStrategy(ABC):
    """Abstract base class for all race strategy controllers."""

    def __init__(self, name: str, description: str, ai_concept: str):
        self.name = name
        self.description = description
        self.ai_concept = ai_concept

    @abstractmethod
    def reset(self, total_laps: int, track_id: str, scenario_name: str) -> None:
        """Called at race initialization or restart."""
        pass

    @abstractmethod
    def decide(self, percepts: Percepts) -> Decision:
        """Called every lap at pit entry decision point to select action."""
        pass
