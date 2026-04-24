from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.db import Base, engine
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Dispose of the engine to clean up connections properly
    await engine.dispose()


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    application.include_router(api_router)
    register_exception_handlers(application)

    @application.get("/")
    async def root():
        return {"message": "FastAPI Async CRUD with MySQL is running"}

    return application


app = create_application()
