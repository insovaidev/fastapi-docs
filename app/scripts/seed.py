import asyncio
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.post import Post

async def seed():
    async with AsyncSessionLocal() as db:
        user = User(name="Dara2", email="dara2@example.com")
        db.add(user)
        await db.commit()
        await db.refresh(user)

        post = Post(
            title="Hello FastAPI",
            content="My first post",
            user_id=user.id
        )

        db.add(post)
        await db.commit()

        print("✅ Seed completed")

if __name__ == "__main__":
    asyncio.run(seed())