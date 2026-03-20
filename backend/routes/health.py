"""routes/health.py"""

from fastapi import APIRouter
from models.schemas import HealthResponse
from services.recommender import recommendation_engine

router = APIRouter(tags=["Health"])

VERSION = "1.0.0"


@router.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        version=VERSION,
        database=True,   # simplified – real DB check done at startup
        ml_model=recommendation_engine.is_fitted,
    )
