🏗 Scenario: Switch Database

app/routes/user.py

@router.post("/", response_model=schema.UserRead)
async def create_user(user: schema.UserCreate, repo: UserRepository = Depends(get_user_repo)):
    return await repo.create(user)

✅ Repository with SQLAlchemy (PostgreSQL)

app/repositories/sqlalchemy_user_repo.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User
from schemas.user import UserCreate

class SQLAlchemyUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: UserCreate) -> User:
        db_user = User(name=user.name, email=user.email)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

✅ Repository with MongoDB (Motor)
from schemas.user import UserCreate, UserResponse
from bson import ObjectId

class MongoUserRepository:
    def __init__(self, db):
        self.collection = db["users"]

    async def create(self, user: UserCreate) -> UserResponse:
        doc = {"name": user.name, "email": user.email}
        result = await self.collection.insert_one(doc)
        return UserResponse(id=str(result.inserted_id), **doc)

    async def get(self, user_id: str) -> UserResponse | None:
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if doc:
            return UserResponse(id=str(doc["_id"]), name=doc["name"], email=doc["email"])

✅ Dependency Injection to Swap Repositories
from fastapi import Depends
from database import get_sqlalchemy_db, get_mongo_db
from repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository
from repositories.mongo_user_repo import MongoUserRepository

# Switch here 👇
USE_DB = "sqlalchemy"   # or "mongo"

async def get_user_repo(db = Depends(get_sqlalchemy_db if USE_DB == "sqlalchemy" else get_mongo_db)):
    if USE_DB == "sqlalchemy":
        return SQLAlchemyUserRepository(db)
    else:
        return MongoUserRepository(db)

✅ Route (Unchanged!)

📂 routes/user.py

from fastapi import APIRouter, Depends
from dependencies import get_user_repo
import schemas.user as schema

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schema.UserRead)
async def create_user(user: schema.UserCreate, repo = Depends(get_user_repo)):
    return await repo.create(user)

@router.get("/{user_id}", response_model=schema.UserRead)
async def read_user(user_id: str, repo = Depends(get_user_repo)):
    return await repo.get(user_id)

# Hint (Here is when u have multiple repo)
from fastapi import Depends
from database import get_sqlalchemy_db, get_mongo_db
from repositories.sqlalchemy_user_repo import SQLAlchemyUserRepository
from repositories.sqlalchemy_post_repo import SQLAlchemyPostRepository
from repositories.mongo_user_repo import MongoUserRepository
from repositories.mongo_post_repo import MongoPostRepository

USE_DB = "sqlalchemy"  # or "mongo"

# 👇 dependency factory
def get_db():
    return get_sqlalchemy_db() if USE_DB == "sqlalchemy" else get_mongo_db()

# User repository
async def get_user_repo(db = Depends(get_db)):
    if USE_DB == "sqlalchemy":
        return SQLAlchemyUserRepository(db)
    else:
        return MongoUserRepository(db)

# Post repository
async def get_post_repo(db = Depends(get_db)):
    if USE_DB == "sqlalchemy":
        return SQLAlchemyPostRepository(db)
    else:
        return MongoPostRepository(db)
