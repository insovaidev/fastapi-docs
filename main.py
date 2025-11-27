from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from database import Base, engine
from routes import user_user_service as user_routes
from routes import test as test_routes
from routes import validation as validation_routes
from routes import exception as exception_routes
from routes import schema as schema_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(test_routes.router)
app.include_router(validation_routes.router)
app.include_router(exception_routes.router)
app.include_router(schema_routes.router)

# 422 - Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        print('error', error)
        field_name = ".".join([str(loc) for loc in error["loc"] if loc != "body"])
        formatted_errors.append({
            "field": field_name,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "One or more validation errors occurred.",
            "errors": formatted_errors
        }
    )

# Generic HTTP Exception Handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    payload = {
        "code": exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
        "message": exc.detail if isinstance(exc.detail, str) else "An error occurred."
    }

    # Add "detail" only for some status codes
    if exc.status_code in [400, 404, 409, 500]:
        payload["detail"] = "Extra information about the error."

    return JSONResponse(
        status_code=exc.status_code,
        content=payload
    )

# Catch-All Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred."
        }
    )

@app.get("/")
def root():
    return {"message": "FastAPI CRUD with MySQL is running"}
