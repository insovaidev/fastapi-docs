from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.user_service import UserService
from app.schemas import user as schema

router = APIRouter(prefix="/users", tags=["Users"])

class UserReadV2(schema.UserRead):
    message: str = "version 2 response model"

@router.get("/{user_id}", response_model=UserReadV2)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_profile(user_id)
    user.message = "version 2 response model"
    return user