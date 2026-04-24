from fastapi import APIRouter

router = APIRouter(prefix="/schema")

@router.get("/")
def schemas_get():
    return {"message": "Hi schema"}
