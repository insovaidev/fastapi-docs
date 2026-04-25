from enum import Enum
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)
from pydantic import BaseModel, ConfigDict, Field


router = APIRouter(prefix="/routes", tags=["Route Learning"])


class Category(str, Enum):
    backend = "backend"
    frontend = "frontend"
    devops = "devops"


class SortBy(str, Enum):
    name = "name"
    price = "price"


class RouteContext(BaseModel):
    trace_id: str | None = None
    session_id: str | None = None
    preview: bool = False


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    category: Category
    description: str | None = Field(default=None, max_length=200)
    tags: list[str] = Field(default_factory=list)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=50)
    price: float | None = Field(default=None, gt=0)
    category: Category | None = None
    description: str | None = Field(default=None, max_length=200)
    tags: list[str] | None = None


class ProductRead(ProductBase):
    id: int
    is_published: bool = False

    model_config = ConfigDict(from_attributes=True)


class BulkLookup(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=10)


class PublishPayload(BaseModel):
    notify_team: bool = True
    note: str | None = Field(default=None, max_length=120)


PRODUCTS: dict[int, dict] = {
    1: {
        "name": "FastAPI Starter",
        "price": 29.0,
        "category": Category.backend,
        "description": "A starter example for route design.",
        "tags": ["fastapi", "api"],
        "is_published": False,
    },
    2: {
        "name": "Frontend Handbook",
        "price": 19.0,
        "category": Category.frontend,
        "description": "Route examples can also document UI APIs.",
        "tags": ["frontend", "docs"],
        "is_published": True,
    },
}
NEXT_PRODUCT_ID = 3


def to_product_read(product_id: int, product: dict) -> ProductRead:
    return ProductRead(id=product_id, **product)


def get_product_or_404(product_id: int) -> dict:
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def get_route_context(
    trace_id: Annotated[str | None, Header(alias="X-Trace-Id")] = None,
    session_id: Annotated[str | None, Cookie()] = None,
    preview: Annotated[bool, Query()] = False,
) -> RouteContext:
    return RouteContext(trace_id=trace_id, session_id=session_id, preview=preview)


def log_publish_action(product_id: int, note: str | None) -> None:
    print(f"Published product {product_id}. note={note}")


@router.get(
    "/",
    summary="Overview of route examples",
    description="Use this endpoint to see what the route-learning module covers.",
)
def get_routes_guide():
    # Request setup: GET /routes/
    # Learn this: a simple starter route that documents the module entry point.
    return {
        "message": "Use these examples to learn FastAPI routing step by step.",
        "topics": [
            "path parameters",
            "query parameters",
            "headers and cookies",
            "dependencies",
            "request body",
            "response model",
            "status codes",
            "GET POST PUT PATCH DELETE",
        ],
        "try_in_docs": [
            "/routes/path-order/me",
            "/routes/path-order/{username}",
            "/routes/search",
            "/routes/context",
            "/routes/products",
            "/routes/products/{product_id}/publish",
        ],
    }


@router.get("/path-order/me", summary="Static route wins when declared first")
def read_my_profile():
    # Request setup: GET /routes/path-order/me
    # Learn this: declare static routes before dynamic routes when paths could overlap.
    return {
        "route_type": "static",
        "message": "This route is matched before /path-order/{username}.",
    }


@router.get("/path-order/{username}", summary="Dynamic path parameter route")
def read_profile_by_username(
    username: Annotated[str, Path(..., min_length=3, max_length=20)],
):
    # Request setup: GET /routes/path-order/insovai
    # Learn this: use Path() to validate and document dynamic URL segments.
    return {
        "route_type": "dynamic",
        "username": username,
    }


@router.get("/search", summary="Query parameter examples")
def search_products(
    q: Annotated[str | None, Query(min_length=2, max_length=30)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
    sort_by: Annotated[SortBy, Query()] = SortBy.name,
    tags: Annotated[list[str] | None, Query()] = None,
):
    # Request setup: GET /routes/search?q=fastapi&page=1&size=5&sort_by=price&tags=api&tags=docs
    # Learn this: Query() is where you add defaults, limits, enums, and repeated values.
    return {
        "q": q,
        "page": page,
        "size": size,
        "sort_by": sort_by,
        "tags": tags or [],
    }


@router.get("/context", summary="Headers, cookies, and dependencies")
def read_request_context(
    context: Annotated[RouteContext, Depends(get_route_context)],
):
    # Request setup: GET /routes/context?preview=true with header X-Trace-Id: abc-123 and cookie session_id=dev-session
    # Learn this: Depends() lets one helper collect headers, cookies, and query values for reuse.
    return {
        "trace_id": context.trace_id,
        "session_id": context.session_id,
        "preview": context.preview,
    }


@router.get("/products", response_model=list[ProductRead], summary="List products")
def list_products(
    category: Annotated[Category | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    # Request setup: GET /routes/products?category=backend&limit=2
    # Learn this: response_model filters output and makes docs clearer for clients.
    items = [to_product_read(product_id, product) for product_id, product in PRODUCTS.items()]
    if category is not None:
        items = [item for item in items if item.category == category]
    return items[:limit]


@router.get(
    "/products/{product_id}",
    response_model=ProductRead,
    summary="Read one product with a path parameter",
)
def read_product(
    product_id: Annotated[int, Path(..., gt=0)],
):
    # Request setup: GET /routes/products/1
    # Learn this: combine a typed path parameter with shared lookup logic and 404 handling.
    product = get_product_or_404(product_id)
    return to_product_read(product_id, product)


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product from a request body",
)
def create_product(product: ProductCreate, response: Response):
    # Request setup: POST /routes/products with JSON {"name":"Routing Mastery","price":49,"category":"backend","description":"Practice routes","tags":["routing","practice"]}
    # Learn this: POST creates data from the request body and can set a 201 status with a Location header.
    global NEXT_PRODUCT_ID

    product_id = NEXT_PRODUCT_ID
    NEXT_PRODUCT_ID += 1
    PRODUCTS[product_id] = {
        **product.model_dump(),
        "is_published": False,
    }
    response.headers["Location"] = f"/routes/products/{product_id}"
    return to_product_read(product_id, PRODUCTS[product_id])


@router.put(
    "/products/{product_id}",
    response_model=ProductRead,
    summary="Full update with PUT",
)
def replace_product(
    product_id: Annotated[int, Path(..., gt=0)],
    product: ProductCreate,
):
    # Request setup: PUT /routes/products/1 with the full JSON body for the product
    # Learn this: PUT usually replaces the full resource, not just one field.
    get_product_or_404(product_id)
    PRODUCTS[product_id] = {
        **product.model_dump(),
        "is_published": PRODUCTS[product_id]["is_published"],
    }
    return to_product_read(product_id, PRODUCTS[product_id])


@router.patch(
    "/products/{product_id}",
    response_model=ProductRead,
    summary="Partial update with PATCH",
)
def update_product(
    product_id: Annotated[int, Path(..., gt=0)],
    product: ProductUpdate,
):
    # Request setup: PATCH /routes/products/1 with JSON {"price":59,"tags":["fastapi","advanced"]}
    # Learn this: PATCH updates only the fields sent by the client.
    current_product = get_product_or_404(product_id)
    updated_fields = product.model_dump(exclude_unset=True)
    current_product.update(updated_fields)
    return to_product_read(product_id, current_product)


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
)
def delete_product(product_id: Annotated[int, Path(..., gt=0)]):
    # Request setup: DELETE /routes/products/1
    # Learn this: DELETE often returns 204 No Content when the resource is removed successfully.
    get_product_or_404(product_id)
    del PRODUCTS[product_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/products/bulk-lookup",
    summary="Body model with a list of ids",
)
def bulk_lookup_products(
    payload: Annotated[BulkLookup, Body(...)]
):
    # Request setup: POST /routes/products/bulk-lookup with JSON {"ids":[1,2,99]}
    # Learn this: a request body can be used for batch operations when query params become too complex.
    found_items = []
    missing_ids = []

    for product_id in payload.ids:
        product = PRODUCTS.get(product_id)
        if product is None:
            missing_ids.append(product_id)
            continue
        found_items.append(to_product_read(product_id, product))

    return {
        "items": found_items,
        "missing_ids": missing_ids,
    }


@router.post(
    "/products/{product_id}/publish",
    summary="Route with body, dependency, and background task",
)
def publish_product(
    product_id: Annotated[int, Path(..., gt=0)],
    payload: PublishPayload,
    background_tasks: BackgroundTasks,
    context: Annotated[RouteContext, Depends(get_route_context)],
):
    # Request setup: POST /routes/products/1/publish?preview=true with header X-Trace-Id: trace-001 and JSON {"notify_team":true,"note":"ready"}
    # Learn this: one route can mix path params, body data, dependencies, and background tasks.
    product = get_product_or_404(product_id)
    product["is_published"] = True

    if payload.notify_team:
        background_tasks.add_task(log_publish_action, product_id, payload.note)

    return {
        "message": "Product published",
        "product_id": product_id,
        "preview_mode": context.preview,
        "trace_id": context.trace_id,
    }
