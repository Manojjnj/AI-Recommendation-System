"""
services/ab_service.py – Lightweight A/B testing for recommendation strategies.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ABTestingService:
    """
    Deterministic A/B assignment: a user is always in the same variant
    for a given experiment (hash-based, no DB required for assignment).
    """

    # Default experiment exposed via the API
    DEFAULT_EXPERIMENT = "rec_strategy_v1"
    DEFAULT_VARIANT_A  = "hybrid"
    DEFAULT_VARIANT_B  = "collaborative"

    def __init__(self) -> None:
        # experiment_name → {variant_a, variant_b, is_active}
        self._experiments: Dict[str, dict] = {
            self.DEFAULT_EXPERIMENT: {
                "variant_a":  self.DEFAULT_VARIANT_A,
                "variant_b":  self.DEFAULT_VARIANT_B,
                "is_active":  True,
                "description": "Compare hybrid vs collaborative filtering",
            }
        }

    def get_variant(self, user_id: int, experiment_name: str = DEFAULT_EXPERIMENT) -> str:
        """
        Return 'A' or 'B' deterministically based on user_id + experiment_name.
        50/50 split.
        """
        exp = self._experiments.get(experiment_name)
        if not exp or not exp["is_active"]:
            return "A"  # fallback to A

        key    = f"{experiment_name}:{user_id}"
        digest = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return "A" if digest % 2 == 0 else "B"

    def get_strategy(self, user_id: int, experiment_name: str = DEFAULT_EXPERIMENT) -> str:
        """Return the recommendation *strategy* string for this user."""
        exp = self._experiments.get(experiment_name)
        if not exp:
            return "hybrid"
        variant = self.get_variant(user_id, experiment_name)
        return exp["variant_a"] if variant == "A" else exp["variant_b"]

    def create_experiment(
        self,
        name:        str,
        variant_a:   str,
        variant_b:   str,
        description: Optional[str] = None,
    ) -> dict:
        self._experiments[name] = {
            "variant_a":  variant_a,
            "variant_b":  variant_b,
            "is_active":  True,
            "description": description or "",
        }
        logger.info("AB experiment created: %s  A=%s B=%s", name, variant_a, variant_b)
        return self._experiments[name]

    def list_experiments(self) -> list:
        return [{"name": k, **v} for k, v in self._experiments.items()]


ab_service = ABTestingService()
