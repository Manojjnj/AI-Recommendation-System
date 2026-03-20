"""
services/recommender.py – Hybrid Recommendation Engine

Implements three strategies:
  1. Collaborative Filtering  – cosine similarity on user-item rating matrix
  2. Content-Based Filtering  – TF-IDF on product descriptions + categories
  3. Hybrid                   – weighted average of both scores
"""

from __future__ import annotations

import logging
import time
from typing import List, Optional, Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────
class RecommendationEngine:
    """
    Stateful recommendation engine.  Call `fit()` once at startup,
    then call `recommend()` for each request.
    """

    # Weight given to the collaborative score in the hybrid blend.
    COLLAB_WEIGHT  = 0.6
    CONTENT_WEIGHT = 0.4

    def __init__(self) -> None:
        self._fitted          = False
        self.df_products:  Optional[pd.DataFrame] = None
        self.df_users:     Optional[pd.DataFrame] = None
        self.df_interactions: Optional[pd.DataFrame] = None

        # Collaborative
        self._user_item_matrix: Optional[pd.DataFrame] = None
        self._user_similarity:  Optional[np.ndarray]   = None

        # Content-based
        self._tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self._product_vectors:  Optional[np.ndarray]      = None

    # ─── Training ───────────────────────────────────────────────

    def fit(
        self,
        df_products:     pd.DataFrame,
        df_users:        pd.DataFrame,
        df_interactions: pd.DataFrame,
    ) -> None:
        t0 = time.perf_counter()

        self.df_products     = df_products.copy()
        self.df_users        = df_users.copy()
        self.df_interactions = df_interactions.copy()

        self._fit_collaborative()
        self._fit_content_based()

        self._fitted = True
        elapsed = time.perf_counter() - t0
        logger.info("✅ RecommendationEngine fitted in %.3fs", elapsed)

    def _fit_collaborative(self) -> None:
        """Build a normalised user-item rating matrix and compute cosine similarity."""
        logger.debug("Fitting collaborative filtering …")

        # Pivot: rows = users, columns = products, values = ratings
        matrix = self.df_interactions.pivot_table(
            index="user_id",
            columns="product_id",
            values="rating",
            aggfunc="mean",
        ).fillna(0.0)

        self._user_item_matrix = matrix
        # Cosine similarity between every pair of users
        self._user_similarity = cosine_similarity(matrix.values)
        logger.debug("  user-item matrix: %s", matrix.shape)

    def _fit_content_based(self) -> None:
        """Vectorise product text with TF-IDF for cosine similarity."""
        logger.debug("Fitting content-based filtering …")

        # Combine category + name + description for richer signal
        corpus = (
            self.df_products["category"].fillna("")
            + " "
            + self.df_products["name"].fillna("")
            + " "
            + self.df_products["description"].fillna("")
        ).tolist()

        self._tfidf_vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
        )
        self._product_vectors = self._tfidf_vectorizer.fit_transform(corpus).toarray()
        logger.debug("  product-vectors: %s", self._product_vectors.shape)

    # ─── Public API ─────────────────────────────────────────────

    def recommend(
        self,
        user_id:  int,
        n:        int = 10,
        strategy: str = "hybrid",
        exclude_seen: bool = True,
    ) -> List[Dict]:
        """
        Return top-N recommended products for *user_id*.

        Parameters
        ----------
        user_id       : int  – target user
        n             : int  – number of products to return
        strategy      : str  – 'collaborative' | 'content' | 'hybrid'
        exclude_seen  : bool – filter out already-rated products

        Returns
        -------
        list of dicts with product fields + score + reason
        """
        if not self._fitted:
            raise RuntimeError("Engine not fitted. Call fit() first.")

        # Products the user has already interacted with
        seen_ids: set[int] = set()
        if exclude_seen:
            seen_ids = set(
                self.df_interactions[self.df_interactions["user_id"] == user_id]["product_id"]
            )

        all_product_ids = list(self.df_products["id"])
        candidates = [p for p in all_product_ids if p not in seen_ids]

        if strategy == "collaborative":
            scores = self._collaborative_scores(user_id, candidates)
            reason = "Users with similar tastes also liked this"
        elif strategy == "content":
            scores = self._content_scores(user_id, candidates)
            reason = "Based on products you've enjoyed"
        else:  # hybrid
            c_scores = self._collaborative_scores(user_id, candidates)
            t_scores = self._content_scores(user_id, candidates)
            scores   = self._blend(c_scores, t_scores, candidates)
            reason   = "Personalised pick for you"

        # Sort by score descending, take top-N
        sorted_candidates = sorted(
            zip(candidates, scores), key=lambda x: x[1], reverse=True
        )[:n]

        results = []
        for pid, score in sorted_candidates:
            row = self.df_products[self.df_products["id"] == pid].iloc[0]
            results.append({
                **row.to_dict(),
                "score":  round(float(score), 4),
                "reason": reason,
            })
        return results

    def similar_products(self, product_id: int, n: int = 6) -> List[Dict]:
        """Return products most similar to *product_id* (content-based)."""
        if not self._fitted:
            raise RuntimeError("Engine not fitted.")

        try:
            idx = self.df_products[self.df_products["id"] == product_id].index[0]
            pid_pos = self.df_products.index.get_loc(idx)
        except (IndexError, KeyError):
            return []

        vec = self._product_vectors[pid_pos].reshape(1, -1)
        sims = cosine_similarity(vec, self._product_vectors)[0]
        sims[pid_pos] = -1  # exclude self

        top_indices = np.argsort(sims)[::-1][:n]
        results = []
        for i in top_indices:
            row = self.df_products.iloc[i]
            results.append({
                **row.to_dict(),
                "score":  round(float(sims[i]), 4),
                "reason": "Similar to products you viewed",
            })
        return results

    def trending_products(self, n: int = 8, days: int = 30) -> List[Dict]:
        """Return products with the most interactions in the last *days* days."""
        if not self._fitted:
            return []

        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        recent = self.df_interactions[
            pd.to_datetime(self.df_interactions["timestamp"]) >= cutoff
        ]

        if recent.empty:
            # Fallback – use all interactions
            recent = self.df_interactions

        popularity = (
            recent.groupby("product_id")
            .agg(
                interaction_count=("product_id", "count"),
                avg_rating=("rating", "mean"),
            )
            .reset_index()
        )
        # Composite trending score: 60% interaction count + 40% avg rating (normalised)
        scaler = MinMaxScaler()
        if len(popularity) > 1:
            popularity[["norm_count", "norm_rating"]] = scaler.fit_transform(
                popularity[["interaction_count", "avg_rating"]].fillna(0)
            )
        else:
            popularity["norm_count"] = 1.0
            popularity["norm_rating"] = 1.0

        popularity["trend_score"] = (
            0.6 * popularity["norm_count"] + 0.4 * popularity["norm_rating"]
        )
        top = popularity.nlargest(n, "trend_score")

        results = []
        for _, row in top.iterrows():
            product_row = self.df_products[self.df_products["id"] == row["product_id"]]
            if product_row.empty:
                continue
            p = product_row.iloc[0].to_dict()
            p["score"]  = round(float(row["trend_score"]), 4)
            p["reason"] = "Trending right now"
            results.append(p)
        return results

    # ─── Score helpers ───────────────────────────────────────────

    def _collaborative_scores(
        self, user_id: int, candidate_ids: List[int]
    ) -> List[float]:
        """
        For the target user, compute a predicted rating for each candidate
        using weighted average of k-nearest neighbours' ratings.
        """
        matrix = self._user_item_matrix

        if user_id not in matrix.index:
            # Cold-start: return popularity-based scores
            return self._popularity_scores(candidate_ids)

        user_pos   = matrix.index.get_loc(user_id)
        user_sims  = self._user_similarity[user_pos]  # shape (n_users,)

        K = 20  # neighbourhood size
        top_k_idx = np.argsort(user_sims)[::-1][1: K + 1]  # exclude self

        scores = []
        for pid in candidate_ids:
            if pid not in matrix.columns:
                scores.append(0.0)
                continue
            col_pos   = matrix.columns.get_loc(pid)
            ratings   = matrix.values[top_k_idx, col_pos]   # neighbours' ratings
            weights   = user_sims[top_k_idx]
            denom     = np.sum(np.abs(weights[ratings > 0]))
            if denom < 1e-9:
                scores.append(0.0)
            else:
                scores.append(
                    float(np.dot(weights[ratings > 0], ratings[ratings > 0]) / denom)
                )
        return self._normalise(scores)

    def _content_scores(
        self, user_id: int, candidate_ids: List[int]
    ) -> List[float]:
        """
        Build a 'user profile vector' from items the user rated highly,
        then score each candidate by cosine similarity to that profile.
        """
        user_interactions = self.df_interactions[
            (self.df_interactions["user_id"] == user_id)
            & (self.df_interactions["rating"] >= 3.5)
        ]

        if user_interactions.empty:
            return self._popularity_scores(candidate_ids)

        # Weighted average of liked product TF-IDF vectors
        profile = np.zeros(self._product_vectors.shape[1])
        total_weight = 0.0
        for _, row in user_interactions.iterrows():
            idx = self.df_products[self.df_products["id"] == row["product_id"]].index
            if not len(idx):
                continue
            pos    = self.df_products.index.get_loc(idx[0])
            weight = float(row["rating"]) if not np.isnan(row["rating"]) else 1.0
            profile      += weight * self._product_vectors[pos]
            total_weight += weight

        if total_weight > 0:
            profile /= total_weight

        # Score every candidate
        candidate_positions = []
        for pid in candidate_ids:
            idx = self.df_products[self.df_products["id"] == pid].index
            candidate_positions.append(
                self.df_products.index.get_loc(idx[0]) if len(idx) else None
            )

        scores = []
        for pos in candidate_positions:
            if pos is None:
                scores.append(0.0)
            else:
                vec   = self._product_vectors[pos].reshape(1, -1)
                score = cosine_similarity(profile.reshape(1, -1), vec)[0][0]
                scores.append(float(score))
        return self._normalise(scores)

    def _blend(
        self,
        collab_scores: List[float],
        content_scores: List[float],
        candidate_ids: List[int],
    ) -> List[float]:
        """Weighted blend of collaborative and content scores."""
        return [
            self.COLLAB_WEIGHT  * c + self.CONTENT_WEIGHT * t
            for c, t in zip(collab_scores, content_scores)
        ]

    def _popularity_scores(self, candidate_ids: List[int]) -> List[float]:
        """Fallback: score by interaction count (cold-start)."""
        counts = self.df_interactions.groupby("product_id").size().to_dict()
        raw    = [float(counts.get(pid, 0)) for pid in candidate_ids]
        return self._normalise(raw)

    @staticmethod
    def _normalise(scores: List[float]) -> List[float]:
        arr = np.array(scores, dtype=float)
        mn, mx = arr.min(), arr.max()
        if mx - mn < 1e-9:
            return [0.0] * len(scores)
        return list((arr - mn) / (mx - mn))

    # ─── State ───────────────────────────────────────────────────

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    def get_stats(self) -> Dict:
        if not self._fitted:
            return {"fitted": False}
        return {
            "fitted":        True,
            "n_users":       len(self.df_users),
            "n_products":    len(self.df_products),
            "n_interactions": len(self.df_interactions),
            "matrix_shape":  list(self._user_item_matrix.shape),
        }


# ─── Module-level singleton ──────────────────────────────────────
recommendation_engine = RecommendationEngine()
