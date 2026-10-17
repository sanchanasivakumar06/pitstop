"""
REST endpoint for multi-race, multi-scenario batch evaluations.
"""

from typing import Dict, Any
from fastapi import APIRouter

from app.schemas.config import EvaluationRequest
from engine.batch import run_batch_evaluation

router = APIRouter()


@router.post("/evaluate")
def evaluate_strategies(req: EvaluationRequest) -> Dict[str, Any]:
    """
    Executes paired-seed Monte Carlo batch simulations comparing AI strategies against baselines.
    Returns statistical aggregates (mean, std, win-rate, consistency) and per-race logs.
    """
    results = run_batch_evaluation(
        strategies=req.strategies,
        scenarios=req.scenarios,
        n_races=req.n_races,
        seeds=req.seeds,
        track_id=req.track_id,
        total_laps=req.total_laps,
    )
    return results
