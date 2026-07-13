from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    phone: str = Field(..., max_length=15)
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    phone: str
    role: str
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
