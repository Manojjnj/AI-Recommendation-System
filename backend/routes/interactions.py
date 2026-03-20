"""routes/interactions.py"""

from fastapi import APIRouter, HTTPException, BackgroundTasks

from models.schemas        import InteractionCreate, InteractionResponse
from services.data_service import data_service
from services.recommender  import recommendation_engine

router = APIRouter(prefix="/interact", tags=["Interactions"])


def _retrain_model():
    """Background task – re-fit the ML engine after a new interaction."""
    recommendation_engine.fit(
        data_service.df_products,
        data_service.df_users,
        data_service.df_interactions,
    )


@router.post("", status_code=201)
async def store_interaction(
    payload:    InteractionCreate,
    background: BackgroundTasks,
):
    """
    Store a user interaction (view / click / purchase / wishlist).
    Triggers asynchronous model retraining so recommendations stay fresh.
    """
    # Validate user + product
    if not data_service.get_user(payload.user_id):
        raise HTTPException(404, f"User {payload.user_id} not found")
    if not data_service.get_product(payload.product_id):
        raise HTTPException(404, f"Product {payload.product_id} not found")

    data_service.add_interaction(
        user_id=payload.user_id,
        product_id=payload.product_id,
        rating=payload.rating,
        interaction_type=payload.interaction_type,
    )

    # Re-train in background so we don't block the response
    background.add_task(_retrain_model)

    return {
        "message":    "Interaction recorded",
        "user_id":    payload.user_id,
        "product_id": payload.product_id,
        "type":       payload.interaction_type,
    }


@router.get("/user/{user_id}")
async def user_interactions(user_id: int, limit: int = 20):
    """Return a user's interaction history."""
    if not data_service.get_user(user_id):
        raise HTTPException(404, f"User {user_id} not found")

    df = data_service.df_interactions
    user_df = df[df["user_id"] == user_id].sort_values("timestamp", ascending=False).head(limit)
    records = []
    for _, row in user_df.iterrows():
        product = data_service.get_product(int(row["product_id"]))
        records.append({
            "product_id":       int(row["product_id"]),
            "product_name":     product["name"] if product else "Unknown",
            "rating":           row["rating"],
            "interaction_type": row["interaction_type"],
            "timestamp":        str(row["timestamp"]),
        })
    return {"user_id": user_id, "interactions": records}
