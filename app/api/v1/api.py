from fastapi import APIRouter

from app.api.v1.endpoints import exception, schemas, test, uploads, users, users_repository, validation

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(users_repository.router)
api_router.include_router(test.router)
api_router.include_router(validation.router)
api_router.include_router(exception.router)
api_router.include_router(schemas.router)
api_router.include_router(uploads.router)
