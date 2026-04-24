# [Router] -> [Service] -> [Repository] -> [Database]

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.repositories.user_repository import UserRepository
from app.schemas import user as schema

router = APIRouter(prefix="/users-repository", tags=["Users Repository"])

@router.post("/", response_model=schema.UserRead)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    new_user = repo.create(user)
    return new_user

@router.get("/", response_model=list[schema.UserRead])
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    return repo.list(skip=skip, limit=limit)
