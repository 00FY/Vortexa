from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from .models import RoleEnum, LeaveStatus, ExpenseStatus

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[RoleEnum] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.EMPLOYEE

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum
    is_active: bool
    class Config:
        orm_mode = True

class EmployeeCreate(BaseModel):
    user_id: int
    full_name: str
    position: Optional[str] = None
    department: Optional[str] = None

class EmployeeRead(BaseModel):
    id: int
    user_id: int
    full_name: str
    position: Optional[str]
    department: Optional[str]
    is_active: bool
    class Config:
        orm_mode = True

class LeaveRequestCreate(BaseModel):
    start_date: datetime
    end_date: datetime
    reason: Optional[str] = None

class LeaveRequestRead(BaseModel):
    id: int
    employee_id: int
    start_date: datetime
    end_date: datetime
    reason: Optional[str]
    status: LeaveStatus
    class Config:
        orm_mode = True

class ExpenseClaimCreate(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class ExpenseClaimRead(BaseModel):
    id: int
    employee_id: int
    amount: float
    description: Optional[str]
    status: ExpenseStatus
    class Config:
        orm_mode = True
