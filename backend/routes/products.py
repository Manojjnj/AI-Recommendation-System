"""routes/products.py"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from services.data_service import data_service
from services.recommender  import recommendation_engine

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("")
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    page:     int           = Query(1, ge=1),
    size:     int           = Query(20, ge=1, le=100),
):
    """Paginated product listing with optional category filter."""
    df = data_service.df_products
    if df is None:
        raise HTTPException(503, "Data not loaded")

    if category:
        df = df[df["category"].str.lower() == category.lower()]

    total  = len(df)
    offset = (page - 1) * size
    page_df = df.iloc[offset: offset + size]

    return {
        "total": total,
        "page":  page,
        "size":  size,
        "items": page_df.to_dict(orient="records"),
    }


@router.get("/categories")
async def list_categories():
    df = data_service.df_products
    if df is None:
        raise HTTPException(503, "Data not loaded")
    cats = sorted(df["category"].unique().tolist())
    return {"categories": cats}


@router.get("/trending")
async def trending_products(
    n:    int = Query(8, ge=1, le=30),
    days: int = Query(30, ge=1, le=365),
):
    """Return trending products based on recent interaction frequency."""
    items = recommendation_engine.trending_products(n=n, days=days)
    return {"items": items}


@router.get("/{product_id}")
async def get_product(product_id: int):
    product = data_service.get_product(product_id)
    if not product:
        raise HTTPException(404, f"Product {product_id} not found")
    return product


@router.get("/{product_id}/similar")
async def similar_products(
    product_id: int,
    n:          int = Query(6, ge=1, le=20),
):
    """Content-based similar products."""
    if not data_service.get_product(product_id):
        raise HTTPException(404, f"Product {product_id} not found")
    items = recommendation_engine.similar_products(product_id, n=n)
    return {"product_id": product_id, "items": items}
