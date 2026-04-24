from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.api.v2.api import api_router as api_router2
from app.db import Base, engine
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup logic (Alembic handles schema migrations)
    yield
    # Dispose of the engine to clean up connections properly
    await engine.dispose()


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan)
    application.include_router(api_router)
    application.include_router(api_router2, prefix="/v2")
    register_exception_handlers(application)

    @application.get("/")
    async def root():
        return {"message": "FastAPI Async CRUD with MySQL is running"}

    return application


app = create_application()
