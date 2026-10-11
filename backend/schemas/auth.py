from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        orm_mode = True