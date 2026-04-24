from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/exceptions", tags=["Exceptions"])

# Basic exception
@router.get("/users/{user_id}")
def get_user(user_id: int, lang: str = "en"):
    if user_id != 1:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {"user_id": user_id, "lang": lang}

# Custom validation
@router.get("/products/{product_id}")
def get_product(product_id: int):
    if product_id not in [1, 2, 3]:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ProductNotFound",
                "message": f"Product with ID {product_id} not found"
            }
        ) 
    return {"product_id": product_id}
