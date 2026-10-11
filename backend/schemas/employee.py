"""backend/schemas/employee.py
Schemas for Employee endpoints.
"""

from datetime import date
from typing import Optional

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
    full_name: Optional[str]
    department: Optional[Department]
    designation: Optional[str]
    phone: Optional[str]
    employee_code: Optional[str]
    date_of_joining: Optional[date]
    manager_id: Optional[str]
    is_active: Optional[bool]

class EmployeeResponse(EmployeeBase):
    id: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
