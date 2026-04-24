from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Use create_async_engine for asynchronous support
# Disabling echo and adding pool_pre_ping to speed up restarts and maintain connections
engine = create_async_engine(
    settings.database_url, 
    echo=False,
    pool_pre_ping=True
)

# Use async_sessionmaker for asynchronous sessions
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,   
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
