from fastapi import APIRouter
# from pydantic import 

router = APIRouter(prefix="/tests", tags=["Tests"])

# Query parameters
@router.get("/search")
def test_search_items(q: str = "", limit: int = 10):
    return {"query": q, "limit": limit}

# Request body 
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float

@router.post("/body")
def test_request_body(item: Item):
    return {"name": item.name,  "price": item.price}

# Route path + query + body
@router.put("/{item_id}")
def update_item(item_id: int, lang: str = None, price: int = None):
    return {"item_id": item_id, "lang": lang, "price": price}

class TestUser(BaseModel):
    name: str
    email: str

@router.get("/response-model1", response_model=TestUser)
def get_response_model():
    return {
        "name":"insovai",
        "email":"insovaidev@gmail.com",
        "password":"@123456"
    }

class TestUser2(BaseModel):
    id: int
    name: str = "guest"
    age: int = None

@router.get("/response-model-exclude-unset/{test_id}", response_model=TestUser2, response_model_exclude_unset=True)
def get_response_model_exclude_unset(test_id: int):
    return TestUser2(id=test_id)

from fastapi.responses import JSONResponse, HTMLResponse

@router.get("/custom-json")
def custom_json():
    return JSONResponse(content={"msg": "Hello"}, status_code=200)

@router.get("/html")
def get_html():
    return HTMLResponse(content="<h1>Hello</h1>")

# Path parameters
@router.get("/{item_id}") 
def test_get(item_id: int):
    return { "message": item_id }

