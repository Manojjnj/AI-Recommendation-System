"""
models/schemas.py – Pydantic v2 schemas for all API request / response payloads.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ────────────────────────────────────────────────────────────────
# Product
# ────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    name:        str
    category:    str
    description: str
    price:       float = Field(..., ge=0)
    image_url:   Optional[str] = None
    stock:       int = Field(default=0, ge=0)
    rating_avg:  Optional[float] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id:         int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="allow")

# ────────────────────────────────────────────────────────────────
# User
# ────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name:  str
    email: EmailStr


class UserResponse(BaseModel):
    id:         int
    name:       str
    email:      str
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ────────────────────────────────────────────────────────────────
# Interaction
# ────────────────────────────────────────────────────────────────

class InteractionCreate(BaseModel):
    user_id:          int
    product_id:       int
    rating:           Optional[float] = Field(None, ge=1.0, le=5.0)
    interaction_type: str = Field(
        default="view",
        pattern="^(view|click|purchase|wishlist)$"
    )


class InteractionResponse(BaseModel):
    id:               int
    user_id:          int
    product_id:       int
    rating:           Optional[float]
    interaction_type: str
    timestamp:        datetime

    model_config = ConfigDict(from_attributes=True)


# ────────────────────────────────────────────────────────────────
# Recommendation
# ────────────────────────────────────────────────────────────────

class RecommendedProduct(ProductResponse):
    score:  float = Field(0.0, description="Recommendation confidence score [0-1]")
    reason: str   = Field("", description="Short human-readable explanation")


class RecommendationResponse(BaseModel):
    user_id:         int
    strategy:        str  # collaborative | content | hybrid
    recommendations: List[RecommendedProduct]
    generated_at:    datetime


# ────────────────────────────────────────────────────────────────
# AB Test
# ────────────────────────────────────────────────────────────────

class ABExperimentCreate(BaseModel):
    name:        str
    description: Optional[str] = None
    variant_a:   str
    variant_b:   str


class ABAssignmentResponse(BaseModel):
    experiment_name: str
    user_id:         int
    variant:         str  # 'A' or 'B'
    strategy:        str  # the actual model name assigned


# ────────────────────────────────────────────────────────────────
# Analytics
# ────────────────────────────────────────────────────────────────

class AnalyticsEventCreate(BaseModel):
    user_id:    Optional[int] = None
    event_type: str
    properties: dict = {}


class DashboardStats(BaseModel):
    total_users:        int
    total_products:     int
    total_interactions: int
    top_categories:     List[dict]
    recent_interactions: List[dict]
    trending_products:  List[dict]


# ────────────────────────────────────────────────────────────────
# Health
# ────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:   str
    version:  str
    database: bool
    ml_model: bool
