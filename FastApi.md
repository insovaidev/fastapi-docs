# All noted that need to build Python FastApi framework

## Cammand Line 
Activate .venv: source .venv/bin/activate
Autolaod: uvicorn main:app --reload

## Routes 
## ✅ 1. What is a Route in FastAPI?
A **route** is a URL path that a client requests. FastAPI calls a function (path operation) to handle it

---

## ✅ 2. Create Your First Route

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")  # route for GET /
def read_root():
    return {"message": "Hello World"}
```

---

## ✅ 3. HTTP Methods (Verbs)

```python
@app.get("/items")
@app.post("/items")
@app.put("/items/{id}")
@app.patch("/items/{id}")
@app.delete("/items/{id}")
```

---

## ✅ 4. Path Parameters

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

---

## ✅ 5. Query Parameters: Bast practic alway Put more specific routes before parameterized routes:

```python
@app.get("/search")
def search_items(q: str = "", limit: int = 10):
    return {"query": q, "limit": limit}
```

---

## ✅ 6. Request Body

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

---

## ✅ 7. Combining Path + Query + Body

```python
@app.put("/items/{item_id}")
def update_item(item_id: int, q: str = None, item: Item = None):
    return {"item_id": item_id, "q": q, "item": item}
```

---

## ✅ 8. Route Tags

```python
@app.get("/users", tags=["users"])
def get_users():
    return [{"name": "Alice"}, {"name": "Bob"}]
```

---

## ✅ 9. Route Summary and Description

```python
@app.get("/users", summary="Get all users", description="Fetch the list of users from the system")
def get_users():
    return []
```

---

## ✅ 10. Route Response Model

```python
class User(BaseModel):
    id: int
    name: str

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}
```

---

## ✅ 11. Optional & Default Parameters

```python
from typing import Optional

@app.get("/items/")
def get_item(q: Optional[str] = None):
    return {"q": q}
```

---

## ✅ 12. Path Parameter Validation

```python
from fastapi import Path

@app.get("/items/{item_id}")
def read_item(item_id: int = Path(..., gt=0, lt=1000)):
    return {"item_id": item_id}
```

---

## ✅ 13. Query Parameter Validation

```python
from fastapi import Query

@app.get("/items/")
def read_items(q: str = Query(..., min_length=3, max_length=10)):
    return {"q": q}
```

---

## ✅ 14. Using APIRouter

```python
# routers/user.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users():
    return ["Alice", "Bob"]

# main.py
from fastapi import FastAPI
from routers import user

app = FastAPI()
app.include_router(user.router)
```

---

## ✅ 15. Route Dependencies

```python
from fastapi import Depends

def get_token():
    return "mysecrettoken"

@app.get("/secure-data")
def secure_data(token: str = Depends(get_token)):
    return {"token": token}
```

---

## ✅ 16. Custom Response

```python
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse

@app.get("/custom-json")
def custom_json():
    return JSONResponse(content={"msg": "Hello"}, status_code=201)

@app.get("/html")
def get_html():
    return HTMLResponse(content="<h1>Hello</h1>")

@app.get("/download")
def download_file():
    return FileResponse("report.pdf")
```

---

## ✅ 17. Route Exception Handling

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id != 1:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id}
```

---

## ✅ 18. Redirects

```python
from fastapi.responses import RedirectResponse

@app.get("/old-path")
def redirect():
    return RedirectResponse(url="/new-path")
```

---

## ✅ 19. Form Data

```python
from fastapi import Form

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

---

## ✅ 20. File Upload

```python
from fastapi import File, UploadFile

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    return {"filename": file.filename}
```

---

## ✅ 21. Headers and Cookies

```python
from fastapi import Header, Cookie

@app.get("/headers")
def get_headers(user_agent: str = Header(None)):
    return {"user_agent": user_agent}

@app.get("/cookies")
def get_cookie(session_id: str = Cookie(None)):
    return {"session_id": session_id}
```

---

## 🧠 Summary Table

| Feature                | Syntax Example                              |
|------------------------|---------------------------------------------|
| Path                  | `@app.get("/users/{id}")`                   |
| Query                 | `?q=value`                                   |
| Request Body          | `def create(item: Item)`                     |
| Route Tag             | `@app.get(..., tags=["tag"])`               |
| Response Model        | `@app.get(..., response_model=User)`        |
| Form Handling         | `username: str = Form(...)`                 |
| File Upload           | `file: UploadFile = File(...)`              |
| Custom Response       | `return JSONResponse(...)`                  |
| Modular Routes        | `APIRouter()` + `include_router(...)`       |
| Dependency Injection  | `Depends(...)`                              |

# Import & Export 
## ✅ Import a function
```
from utils.auth import verify_token 
```
## ✅ Import multiple things
```
from utils.auth import verify_token, 
```
