from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services.user_service import UserService
from app.schemas import user as schema

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schema.UserRead)
async def create_user(user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.register_user(user)

@router.get("/", response_model=list[schema.UserRead])
async def list_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.list_active_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=schema.UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    return await service.get_user_profile(user_id)

@router.put("/{user_id}", response_model=schema.UserRead)
async def update(user_id: int, user: schema.UserCreate, db: AsyncSession = Depends(get_db)):
    # You could also add an update method to UserService
    from app.repositories import user as repositories
    db_user = await repositories.update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}", response_model=schema.UserRead)
async def delete(user_id: int, db: AsyncSession = Depends(get_db)):
    from app.repositories import user as repositories
    db_user = await repositories.delete_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
