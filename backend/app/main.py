"""
app/main.py – FastAPI application factory.

Startup sequence:
  1. Load CSV data into DataService
  2. Fit the RecommendationEngine
  3. Register all routers
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Make sure project root is on sys.path when running directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from services.data_service import data_service
from services.recommender  import recommendation_engine
from routes.health          import router as health_router
from routes.products        import router as products_router
from routes.recommendations import router as rec_router
from routes.interactions    import router as interact_router
from routes.users           import router as users_router
from routes.analytics       import router as analytics_router

# ────────────────────────────────────────────────────────────────
# Logging
# ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────
    logger.info("🚀 Starting E-commerce Recommendation API …")
    try:
        data_service.load()
        recommendation_engine.fit(
            data_service.df_products,
            data_service.df_users,
            data_service.df_interactions,
        )
        logger.info("✅ ML engine ready")
    except Exception as exc:
        logger.error("❌ Startup error: %s", exc, exc_info=True)

    yield  # application runs

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("👋 Shutting down …")


# ────────────────────────────────────────────────────────────────
# Application
# ────────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="E-commerce Recommendation API",
        description=(
            "Hybrid ML recommendation system combining collaborative "
            "filtering and content-based filtering."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ───────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(products_router)
    app.include_router(rec_router)
    app.include_router(interact_router)
    app.include_router(users_router)
    app.include_router(analytics_router)

    return app


app = create_app()


# ── Local dev entry point ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
