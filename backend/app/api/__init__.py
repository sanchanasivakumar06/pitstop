"""
API routers package.
"""

from fastapi import APIRouter
from app.api.races import router as races_router
from app.api.strategies import router as strategies_router
from app.api.evaluate import router as evaluate_router

api_router = APIRouter()
api_router.include_router(races_router, prefix="/races", tags=["Races"])
api_router.include_router(strategies_router, tags=["Metadata"])
api_router.include_router(evaluate_router, tags=["Evaluation"])
