from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    user_name: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
