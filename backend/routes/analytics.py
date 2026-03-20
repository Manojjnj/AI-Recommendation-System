"""routes/analytics.py"""

from fastapi import APIRouter
from services.data_service import data_service
from services.recommender  import recommendation_engine
from services.ab_service   import ab_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def dashboard():
    """Return aggregate statistics for the admin dashboard."""
    stats   = data_service.get_analytics()
    ml_info = recommendation_engine.get_stats()
    trending = recommendation_engine.trending_products(n=5)

    return {
        **stats,
        "ml_stats":         ml_info,
        "trending_products": trending,
        "ab_experiments":   ab_service.list_experiments(),
    }


@router.get("/model-stats")
async def model_stats():
    return recommendation_engine.get_stats()
