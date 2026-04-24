from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        field_name = ".".join([str(loc) for loc in error["loc"] if loc != "body"])
        formatted_errors.append(
            {
                "field": field_name,
                "message": error["msg"],
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "One or more validation errors occurred.",
            "errors": formatted_errors,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    payload = {
        "code": exc.detail if isinstance(exc.detail, str) else "HTTP_ERROR",
        "message": exc.detail if isinstance(exc.detail, str) else "An error occurred.",
    }

    if exc.status_code in [400, 404, 409, 500]:
        payload["detail"] = "Extra information about the error."

    return JSONResponse(
        status_code=exc.status_code,
        content=payload,
    )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        },
    )


def register_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    application.add_exception_handler(
        Exception,
        global_exception_handler,
    )
