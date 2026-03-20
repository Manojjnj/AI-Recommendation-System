"""routes/recommendations.py"""

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from services.recommender import recommendation_engine
from services.data_service import data_service
from services.ab_service   import ab_service
from models.schemas        import RecommendationResponse

router = APIRouter(prefix="/recommend", tags=["Recommendations"])

StrategyType = Literal["hybrid", "collaborative", "content"]


@router.get("/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id:  int,
    n:        int          = Query(10, ge=1, le=50, description="Number of recommendations"),
    strategy: StrategyType = Query("hybrid", description="Recommendation strategy"),
    ab_test:  bool         = Query(False, description="Use A/B experiment strategy"),
):
    """
    Return top-N personalised product recommendations for *user_id*.

    If `ab_test=true` the strategy is determined by the A/B experiment
    assigned to this user (ignoring the `strategy` query parameter).
    """
    if not recommendation_engine.is_fitted:
        raise HTTPException(503, "Recommendation model not ready")

    # Check user exists (warn but don't block – cold start still works)
    user = data_service.get_user(user_id)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")

    # Optionally override strategy via A/B test assignment
    if ab_test:
        strategy = ab_service.get_strategy(user_id)  # type: ignore[assignment]

    try:
        items = recommendation_engine.recommend(
            user_id=user_id,
            n=n,
            strategy=strategy,
        )
    except Exception as exc:
        raise HTTPException(500, f"Recommendation error: {exc}") from exc

    return RecommendationResponse(
        user_id=user_id,
        strategy=strategy,
        recommendations=items,  # type: ignore[arg-type]
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/{user_id}/ab-variant")
async def get_ab_variant(user_id: int, experiment: str = "rec_strategy_v1"):
    """Expose which A/B variant the user is assigned to."""
    variant  = ab_service.get_variant(user_id, experiment)
    strategy = ab_service.get_strategy(user_id, experiment)
    return {
        "user_id":    user_id,
        "experiment": experiment,
        "variant":    variant,
        "strategy":   strategy,
    }
