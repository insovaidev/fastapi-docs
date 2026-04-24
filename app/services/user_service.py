from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.repositories.user import get_user, get_users, create_user, update_user, delete_user
from app.schemas.user import UserCreate

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserCreate):
        """
        Example of business logic in a service:
        1. Check if user already exists (Business Rule)
        2. Perform the creation
        3. Could add more steps like sending emails or logs
        """
        # Business logic: check for existing email
        existing_user = await self.db.execute(
            # Using a simple check here, but could be a repo call
            # For simplicity, we'll just use the create_user repo and handle integrity errors
            # or check manually first.
        )
        
        # Here we just wrap the repo call but we could add complex logic
        return await create_user(self.db, user_data)

    async def get_user_profile(self, user_id: int):
        user = await get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        return user


    async def get_user_profile_v2(self, user_id: int):
        user = await get_user(self.db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")
        return user


    async def list_active_users(self, skip: int = 0, limit: int = 10):
        # Could add logic to only list 'active' users
        return await get_users(self.db, skip, limit)
