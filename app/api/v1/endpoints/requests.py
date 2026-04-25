from __future__ import annotations

from enum import Enum
from typing import Annotated, Any
from uuid import uuid4

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field


router = APIRouter(prefix="/requests", tags=["Request Mastery"])


class Environment(str, Enum):
    local = "local"
    staging = "staging"
    production = "production"


class PaginationQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)
    search: str | None = Field(default=None, min_length=2, max_length=50)


class ContactCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    message: str = Field(..., min_length=10, max_length=1000)
    tags: list[str] = Field(default_factory=list, max_length=5)


class WebhookEvent(BaseModel):
    event: str = Field(..., min_length=3, max_length=50)
    resource_id: str = Field(..., min_length=1, max_length=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


CONTACT_MESSAGES: list[dict[str, Any]] = []
PAYMENT_REQUESTS: dict[str, dict[str, Any]] = {}


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
    search: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
) -> PaginationQuery:
    return PaginationQuery(page=page, size=size, search=search)


def attach_request_id(
    request: Request,
    x_request_id: Annotated[str | None, Header(alias="X-Request-Id")] = None,
) -> str:
    request_id = x_request_id or str(uuid4())
    request.state.request_id = request_id
    return request_id


def require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-Api-Key")] = None,
) -> str:
    if x_api_key != "dev-secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Api-Key",
        )
    return x_api_key


@router.get("/", summary="Guide to request handling examples")
async def get_request_guide():
    # Request setup: GET /requests/
    # Learn this: start with a guide route so people know what request-handling topics this module covers.
    return {
        "message": "These routes focus on how a real FastAPI app reads and handles requests.",
        "topics": [
            "request metadata",
            "path/query/header/cookie reading",
            "json body handling",
            "html form handling",
            "idempotency for POST requests",
            "content negotiation",
            "webhook verification",
            "request state and correlation ids",
        ],
        "try_in_docs": [
            "/requests/inspect",
            "/requests/search?page=1&size=5&search=api",
            "/requests/profile",
            "/requests/content",
            "/requests/contacts",
            "/requests/payments",
            "/requests/webhooks/payment",
        ],
    }


@router.get("/inspect", summary="Inspect the raw incoming request")
async def inspect_request(
    request: Request,
    request_id: Annotated[str, Depends(attach_request_id)],
):
    # Request setup: GET /requests/inspect with optional header X-Request-Id: req-123
    # Learn this: use the Request object when you need low-level details like URL, client info, and raw headers.
    forwarded_for = request.headers.get("x-forwarded-for")
    return {
        "method": request.method,
        "url": str(request.url),
        "base_url": str(request.base_url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client": {
            "host": request.client.host if request.client else None,
            "port": request.client.port if request.client else None,
            "forwarded_for": forwarded_for,
        },
        "headers_subset": {
            "host": request.headers.get("host"),
            "user_agent": request.headers.get("user-agent"),
            "accept": request.headers.get("accept"),
        },
        "request_id": request_id,
    }


@router.get("/search", summary="Query handling for listing endpoints")
async def search_requests(
    filters: Annotated[PaginationQuery, Depends(get_pagination)],
    environment: Annotated[Environment, Query()] = Environment.local,
    include_archived: Annotated[bool, Query()] = False,
):
    # Request setup: GET /requests/search?page=1&size=5&search=api&environment=staging&include_archived=true
    # Learn this: collect query params into a dependency or model when list endpoints start growing in complexity.
    return {
        "filters": filters.model_dump(),
        "environment": environment,
        "include_archived": include_archived,
        "note": "In a real app these values usually drive database filtering and pagination.",
    }


@router.get("/profile", summary="Read headers and cookies like a real authenticated request")
async def read_request_profile(
    request: Request,
    request_id: Annotated[str, Depends(attach_request_id)],
    authorization: Annotated[str | None, Header()] = None,
    session_id: Annotated[str | None, Cookie()] = None,
    locale: Annotated[str | None, Header(alias="X-Locale")] = None,
):
    # Request setup: GET /requests/profile with Authorization: Bearer token or cookie session_id=abc plus X-Locale: en
    # Learn this: real apps usually mix headers, cookies, and request state to build auth and user context.
    is_authenticated = bool(authorization or session_id)
    return {
        "authenticated": is_authenticated,
        "auth_source": "authorization-header" if authorization else "session-cookie" if session_id else None,
        "session_id": session_id,
        "locale": locale or "en",
        "request_id": request_id,
        "docs_tip": "Real apps often combine headers, cookies, and request.state for auth and tracing.",
        "path": request.url.path,
    }


@router.post(
    "/contacts",
    status_code=status.HTTP_201_CREATED,
    summary="Handle a normal JSON body from a frontend client",
)
async def create_contact_message(
    payload: ContactCreate,
    request: Request,
    response: Response,
    request_id: Annotated[str, Depends(attach_request_id)],
):
    # Request setup: POST /requests/contacts with JSON {"full_name":"Ada Lovelace","email":"ada@example.com","message":"I want help with FastAPI requests","tags":["docs"]}
    # Learn this: this is the common API shape for frontend requests, where validated JSON becomes a typed payload object.
    message_id = len(CONTACT_MESSAGES) + 1
    record = {
        "id": message_id,
        **payload.model_dump(),
        "request_id": request_id,
        "client_host": request.client.host if request.client else None,
    }
    CONTACT_MESSAGES.append(record)
    response.headers["Location"] = f"/requests/contacts/{message_id}"
    return {
        "message": "Contact request accepted",
        "data": record,
    }


@router.get("/contacts/{message_id}", summary="Read a stored JSON request result")
async def read_contact_message(message_id: int):
    # Request setup: GET /requests/contacts/1
    # Learn this: after creating a resource, expose a follow-up read route that clients can use with the returned id.
    for item in CONTACT_MESSAGES:
        if item["id"] == message_id:
            return item
    raise HTTPException(status_code=404, detail="Contact message not found")


@router.post("/forms/feedback", summary="Handle HTML form data")
async def submit_feedback_form(
    name: Annotated[str, Form(min_length=2, max_length=50)],
    email: Annotated[str, Form(min_length=5, max_length=150)],
    message: Annotated[str, Form(min_length=10, max_length=500)],
):
    # Request setup: POST /requests/forms/feedback as form-data or application/x-www-form-urlencoded
    # Learn this: not every request is JSON; admin screens and classic HTML forms still submit form fields.
    return {
        "message": "Form submitted successfully",
        "data": {
            "name": name,
            "email": email,
            "message": message,
        },
        "why_it_matters": "Traditional server-rendered apps and admin panels still send form-encoded requests.",
    }


@router.post(
    "/payments",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Handle idempotent POST requests safely",
)
async def create_payment_request(
    request: Request,
    amount: Annotated[float, Query(gt=0)],
    currency: Annotated[str, Query(min_length=3, max_length=3)] = "USD",
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    _: Annotated[str, Depends(require_api_key)] = "dev-secret",
):
    # Request setup: POST /requests/payments?amount=99.5&currency=usd with X-Api-Key: dev-secret and Idempotency-Key: payment-001
    # Learn this: use headers like Idempotency-Key for operations that must not be processed twice on client retries.
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required",
        )

    existing = PAYMENT_REQUESTS.get(idempotency_key)
    if existing is not None:
        return {
            "message": "Existing payment request returned from idempotency store",
            "data": existing,
        }

    payment_id = f"pay_{uuid4().hex[:12]}"
    payload = {
        "payment_id": payment_id,
        "amount": amount,
        "currency": currency.upper(),
        "created_from": request.client.host if request.client else None,
        "status": "queued",
    }
    PAYMENT_REQUESTS[idempotency_key] = payload
    return {
        "message": "Payment request accepted",
        "data": payload,
    }


@router.get("/content", summary="Return HTML or JSON based on the Accept header")
async def get_content_by_accept_header(request: Request):
    # Request setup: GET /requests/content with Accept: text/html or Accept: application/json
    # Learn this: the Accept header lets one endpoint return different representations for different clients.
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        html = """
        <html>
            <body>
                <h1>Request Content Negotiation</h1>
                <p>The client asked for HTML, so this endpoint returned HTML.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html.strip())

    return JSONResponse(
        content={
            "message": "The client asked for JSON or did not request HTML explicitly.",
            "accept": accept,
        }
    )


@router.post("/webhooks/payment", summary="Handle an external webhook request")
async def receive_payment_webhook(
    event: WebhookEvent,
    request: Request,
    x_signature: Annotated[str | None, Header(alias="X-Signature")] = None,
):
    # Request setup: POST /requests/webhooks/payment with header X-Signature: demo-signature and a JSON event body
    # Learn this: webhook endpoints usually verify a signature header before trusting the incoming payload.
    if x_signature != "demo-signature":
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    return {
        "message": "Webhook accepted",
        "event": event.model_dump(),
        "source_ip": request.client.host if request.client else None,
        "headers_checked": ["X-Signature"],
    }
