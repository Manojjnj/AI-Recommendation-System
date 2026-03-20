"""routes/users.py"""

from fastapi import APIRouter, HTTPException
from models.schemas import UserResponse
from services.data_service import data_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = data_service.get_user(user_id)
    if not user:
        raise HTTPException(404, f"User {user_id} not found")
    # Augment with defaults for schema fields missing in CSV
    user.setdefault("avatar_url", None)
    user.setdefault("created_at", "2024-01-01T00:00:00Z")
    return user


@router.get("")
async def list_users(page: int = 1, size: int = 20):
    df     = data_service.df_users
    total  = len(df)
    offset = (page - 1) * size
    items  = df.iloc[offset: offset + size].to_dict(orient="records")
    return {"total": total, "page": page, "size": size, "items": items}
