from fastapi import APIRouter

router = APIRouter(prefix="/schemas")

@router.get("/")
def schemas_get():
    return {"message": "Hi schema"}
