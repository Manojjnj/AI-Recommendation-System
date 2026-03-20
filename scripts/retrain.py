#!/usr/bin/env python3
"""
scripts/retrain.py – Standalone model retraining script.

Usage:
    python scripts/retrain.py
    python scripts/retrain.py --output-dir backend/model_cache

Loads the latest CSV data, re-fits the recommendation engine,
and serialises it to disk so the API can hot-reload it.

Can also be wired up as a cron job or Celery task for scheduled retraining.
"""

import argparse
import logging
import pickle
import sys
import time
from pathlib import Path

# Make sure project root is on path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("retrain")


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Load data ────────────────────────────────────────────
    log.info("Loading data …")
    from services.data_service import DataService
    ds = DataService()
    ds.load()

    log.info(
        "  %d products, %d users, %d interactions",
        len(ds.df_products),
        len(ds.df_users),
        len(ds.df_interactions),
    )

    # ── 2. Fit engine ────────────────────────────────────────────
    log.info("Fitting recommendation engine …")
    from services.recommender import RecommendationEngine
    engine = RecommendationEngine()

    t0 = time.perf_counter()
    engine.fit(ds.df_products, ds.df_users, ds.df_interactions)
    elapsed = time.perf_counter() - t0
    log.info("  Fitting complete in %.3fs", elapsed)

    # ── 3. Smoke-test ─────────────────────────────────────────────
    log.info("Running smoke tests …")
    for strat in ("collaborative", "content", "hybrid"):
        recs = engine.recommend(user_id=1, n=5, strategy=strat)
        assert len(recs) > 0, f"No recommendations for strategy={strat}"
        log.info("  %s → %s", strat, [r["name"][:25] for r in recs[:3]])

    trending = engine.trending_products(n=3)
    assert len(trending) > 0, "No trending products"
    log.info("  trending → %s", [t["name"][:25] for t in trending])

    # ── 4. Serialise ─────────────────────────────────────────────
    model_path = output_dir / "recommendation_engine.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(engine, f, protocol=pickle.HIGHEST_PROTOCOL)

    size_kb = model_path.stat().st_size / 1024
    log.info("✅ Model saved to %s (%.1f KB)", model_path, size_kb)

    # ── 5. Print stats ────────────────────────────────────────────
    stats = engine.get_stats()
    log.info("Model stats: %s", stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain the recommendation engine")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "backend" / "model_cache"),
        help="Directory to write the serialised model (default: backend/model_cache)",
    )
    args = parser.parse_args()
    main(Path(args.output_dir))
