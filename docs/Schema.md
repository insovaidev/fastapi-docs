app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional

# Input schema (used for creating users)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)

    # custom validator (no "admin" usernames allowed)
    @field_validator("username")
    def no_admin_username(cls, v):
        if v.lower() == "admin":
            raise ValueError("Username 'admin' is not allowed")
        return v


# Response schema (hide password)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True   # ✅ required in Pydantic v2 for ORM models

✅ Key points:
Field() gives validation rules (min, max, constraints).

EmailStr auto-validates emails.

field_validator for custom rules.

UserResponse only exposes safe fields, never the password.




