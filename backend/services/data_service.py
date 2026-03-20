"""
services/data_service.py – CSV loader, preprocessor, and in-memory data store.

In production, this layer would read from PostgreSQL.  For portability this
implementation reads from CSV files and optionally syncs to the DB.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


class DataService:
    """Loads, validates and exposes the three core DataFrames."""

    def __init__(self) -> None:
        self.df_products:     Optional[pd.DataFrame] = None
        self.df_users:        Optional[pd.DataFrame] = None
        self.df_interactions: Optional[pd.DataFrame] = None
        self._loaded = False

    # ─── Public ─────────────────────────────────────────────────

    def load(self) -> None:
        logger.info("Loading data from %s …", DATA_DIR)
        self.df_products     = self._load_products()
        self.df_users        = self._load_users()
        self.df_interactions = self._load_interactions()
        self._loaded = True
        logger.info(
            "Data loaded: %d products, %d users, %d interactions",
            len(self.df_products),
            len(self.df_users),
            len(self.df_interactions),
        )

    def add_interaction(
        self,
        user_id:          int,
        product_id:       int,
        rating:           Optional[float],
        interaction_type: str = "view",
    ) -> None:
        """Append a new interaction record to the in-memory store."""
        new_row = pd.DataFrame([{
            "user_id":          user_id,
            "product_id":       product_id,
            "rating":           rating,
            "interaction_type": interaction_type,
            "timestamp":        pd.Timestamp.now(),
        }])
        # Upsert: if (user_id, product_id) already exists, update rating
        mask = (
            (self.df_interactions["user_id"] == user_id)
            & (self.df_interactions["product_id"] == product_id)
        )
        if mask.any():
            if rating is not None:
                self.df_interactions.loc[mask, "rating"] = rating
            self.df_interactions.loc[mask, "interaction_type"] = interaction_type
            self.df_interactions.loc[mask, "timestamp"] = pd.Timestamp.now()
        else:
            self.df_interactions = pd.concat(
                [self.df_interactions, new_row], ignore_index=True
            )

    def get_product(self, product_id: int) -> Optional[dict]:
        row = self.df_products[self.df_products["id"] == product_id]
        return row.iloc[0].to_dict() if not row.empty else None

    def get_user(self, user_id: int) -> Optional[dict]:
        row = self.df_users[self.df_users["id"] == user_id]
        return row.iloc[0].to_dict() if not row.empty else None

    def get_analytics(self) -> dict:
        """Quick dashboard stats from in-memory DataFrames."""
        if not self._loaded:
            return {}

        # Top categories by interaction count
        merged = pd.merge(
            self.df_interactions,
            self.df_products[["id", "category"]],
            left_on="product_id",
            right_on="id",
        )
        top_cats = (
            merged.groupby("category")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(5)
            .to_dict(orient="records")
        )

        # Recent interactions
        recent = (
            self.df_interactions.sort_values("timestamp", ascending=False)
            .head(10)
            .to_dict(orient="records")
        )

        return {
            "total_users":        len(self.df_users),
            "total_products":     len(self.df_products),
            "total_interactions": len(self.df_interactions),
            "top_categories":     top_cats,
            "recent_interactions": recent,
        }

    # ─── Loaders ────────────────────────────────────────────────

    def _load_products(self) -> pd.DataFrame:
        path = DATA_DIR / "products.csv"
        df = pd.read_csv(path)
        df = df.dropna(subset=["id", "name", "description"])
        df["id"]        = df["id"].astype(int)
        df["price"]     = pd.to_numeric(df["price"], errors="coerce").fillna(0.0)
        df["stock"]     = pd.to_numeric(df["stock"], errors="coerce").fillna(0).astype(int)
        df["rating_avg"] = pd.to_numeric(df.get("rating_avg", np.nan), errors="coerce").fillna(4.0)
        df["description"] = df["description"].str.strip()
        logger.debug("  products shape: %s", df.shape)
        return df.reset_index(drop=True)

    def _load_users(self) -> pd.DataFrame:
        path = DATA_DIR / "users.csv"
        df = pd.read_csv(path)
        df = df.dropna(subset=["id", "email"])
        df["id"] = df["id"].astype(int)
        logger.debug("  users shape: %s", df.shape)
        return df.reset_index(drop=True)

    def _load_interactions(self) -> pd.DataFrame:
        path = DATA_DIR / "interactions.csv"
        df = pd.read_csv(path)
        df = df.dropna(subset=["user_id", "product_id"])
        df["user_id"]    = df["user_id"].astype(int)
        df["product_id"] = df["product_id"].astype(int)
        df["rating"]     = pd.to_numeric(df["rating"], errors="coerce")
        # Clamp ratings
        df["rating"] = df["rating"].clip(lower=1.0, upper=5.0)
        df["timestamp"] = pd.to_datetime(df.get("timestamp", pd.Timestamp.now()), errors="coerce")
        df["interaction_type"] = df.get("interaction_type", "view").fillna("view")
        logger.debug("  interactions shape: %s", df.shape)
        return df.reset_index(drop=True)


# Module-level singleton
data_service = DataService()
