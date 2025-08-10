from fastapi import APIRouter
# from pydantic import 

router = APIRouter(prefix="/tests", tags=["Tests"])

# Query parameters
@router.get("/search")
def test_search_items(q: str = "", limit: int = 10):
    return {"query": q, "limit": limit}

# Path parameters
@router.get("/{item_id}") 
def test_get(item_id: int):
    return { "message": item_id }

# Request body 
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float

@router.post("/body")
def test_request_body(item: Item):
    return {"name": item.name,  "price": item.price}


