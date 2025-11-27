from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
import json


router = APIRouter(prefix="/validations", tags=["Validations"])

# Basic query parameter validation
@router.get("/items")
def get_items(
    lang: Optional[str] = Query(None, min_length=2,  max_length=10)
):
    return {"lang": lang}

# Required query parameters
@router.get("/search")
def search(lang: str = Query(..., min_length=2)):
    return {"lang": lang}

# Default parameters + Constraint
@router.get("/items/")
def get_items(
    page: int = Query(1, ge=1),    # >= 1
    size: int = Query(10, le=100)  # <= 100
):
    return {"page": page, "size": size}

# Regex Validation
@router.get("/validate")
def validate_username(
    username: str = Query(..., regex="^[a-zA-Z0-9_]{3,20}$")
):
    return {"username": username}

# Lists & Multiple Values
@router.get("/tags/")
def get_tags(
    tags: list[str] = Query(["default"], min_length=2)
):
    return {"tags": tags}

# GET /tags/?tags=python&tags=fastapi
# → {"tags": ["python", "fastapi"]}

# Aliases for Query Params
@router.get("/items/")
def get_items(
    q: str = Query(..., alias="search-term")
):
    return {"q": q}
# GET /items/?search-term=phone → q="phone"

# Deprecating Query Params
@router.get("/items/")
def get_items(
    old_param: Optional[str] = Query(None, deprecated=True)
):
    return {"old_param": old_param}

# Combining Query Validation with Pydantic Models

class ItemQuery(BaseModel):
    q: Optional[str] = Field(None, min_length=3, max_length=10)
    page: int = Field(1, ge=1)
    size: int = Field(10, le=100)

@router.get("/items/")
def get_items(params: ItemQuery = Depends()):
    return params

# Complex Types in Query Params
# You can even parse JSON in query params:
@router.get("/filters")
def get_filters(
    filters: str = Query(...)
):
    filters_dict = json.loads(filters)
    return filters_dict
    
# Security & Safe Query Params    
@router.get("/search2")
def search(
    q: str = Query(..., min_length=1, max_length=50, strip_whitespace=True)
):
    return {"q": q.strip()}
# Prevents blank searches and trims spaces

# Combining with Annotated (Python 3.9+ clean syntax)
from typing import Annotated

@router.get("/products")
def get_products(
    q: Annotated[Optional[str], Query(min_length=3)] = None,
    page: Annotated[int, Query(ge=1)] = 1
):
    return {"q": q, "page": page}
# This keeps type hints clean while attaching validation

# Advanced: Dynamic Validation
@router.get("/range")
def get_range(
    start: int = Query(...),
    end: int = Query(...)
):
    if end <= start:
        raise HTTPException(400, "end must be greater than start")
    return {"range": (start, end)}

# Enum validation for Query params
from enum import Enum
class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@router.get("/enum")
def enum(order: SortOrder = Query(...)):
    return {"order": order}
