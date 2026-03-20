"""
database/models.py – SQLAlchemy ORM table definitions.
Mirrors schema.sql but managed by SQLAlchemy for application use.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean,
    ForeignKey, DateTime, UniqueConstraint, Index, JSON
)
from sqlalchemy.orm import relationship
from .connection import Base


def utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(120), nullable=False)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url    = Column(Text, nullable=True)
    created_at    = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at    = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    interactions  = relationship("Interaction", back_populates="user", lazy="selectin")


# ---------------------------------------------------------------------------
class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(255), nullable=False)
    category    = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    price       = Column(Numeric(10, 2), nullable=False)
    image_url   = Column(Text, nullable=True)
    stock       = Column(Integer, default=0, nullable=False)
    rating_avg  = Column(Numeric(3, 2), default=0.0)
    created_at  = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at  = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    interactions = relationship("Interaction", back_populates="product", lazy="selectin")


# ---------------------------------------------------------------------------
class Interaction(Base):
    __tablename__ = "interactions"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_product"),
    )

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id       = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    rating           = Column(Numeric(3, 1), nullable=True)
    interaction_type = Column(String(20), default="view", nullable=False)
    timestamp        = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user    = relationship("User",    back_populates="interactions")
    product = relationship("Product", back_populates="interactions")


# ---------------------------------------------------------------------------
class ABExperiment(Base):
    __tablename__ = "ab_experiments"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    variant_a   = Column(String(80), nullable=False)
    variant_b   = Column(String(80), nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)
    created_at  = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    assignments = relationship("ABAssignment", back_populates="experiment")


class ABAssignment(Base):
    __tablename__ = "ab_assignments"
    __table_args__ = (
        UniqueConstraint("experiment_id", "user_id", name="uq_exp_user"),
    )

    id            = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey("ab_experiments.id", ondelete="CASCADE"))
    user_id       = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    variant       = Column(String(1), nullable=False)
    assigned_at   = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    experiment = relationship("ABExperiment", back_populates="assignments")


# ---------------------------------------------------------------------------
class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_type = Column(String(50), nullable=False)
    properties = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
