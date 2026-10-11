from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from uuid import UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserProfileResponse(BaseModel):
    id: Union[UUID, str]
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True
        orm_mode = True