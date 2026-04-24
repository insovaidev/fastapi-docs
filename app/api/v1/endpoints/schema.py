from fastapi import APIRouter

router = APIRouter(prefix="/schema")

@router.get("/")
def schema_get():
    return {"message": "Hi schema"}
