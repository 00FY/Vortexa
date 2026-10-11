"""backend/schemas/employee.py
Schemas for Employee endpoints.
"""

from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field
from models.employee import Department


class EmployeeBase(BaseModel):
    full_name: str = Field(..., example="John Doe")
    department: Department = Field(..., example=Department.ENGINEERING)
    designation: str = Field(..., example="Backend Engineer")
    phone: Optional[str] = Field(None, example="+1-555-0100")
    employee_code: str = Field(..., example="EMP001")
    date_of_joining: date = Field(..., example="2023-01-15")


class EmployeeCreate(EmployeeBase):
    manager_id: Optional[str] = Field(None, description="UUID of manager")


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[Department] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    employee_code: Optional[str] = None
    date_of_joining: Optional[date] = None
    manager_id: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: Union[UUID, str]
    is_active: bool
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]

    class Config:
        from_attributes = True
        orm_mode = True
