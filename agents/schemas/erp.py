from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class ERPUserRole(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    HR_ADMIN = "HR_ADMIN"

class ERPUserContext(BaseModel):
    employee_id: str = Field(..., description="Unique employee identifier verified from ERP session")
    name: str = Field(..., description="Full employee name")
    email: str = Field(..., description="Official corporate email")
    role: ERPUserRole = Field(..., description="Authorized role from ERP directory")
    department: str = Field(..., description="Department or business unit")
    manager_id: Optional[str] = Field(None, description="Direct reporting manager ID")
    token: Optional[str] = Field(None, description="Bearer JWT token for downstream ERP calls")

class LeaveStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

class LeaveRecord(BaseModel):
    leave_id: str
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    days_count: float
    reason: str
    status: LeaveStatus

class ExpenseStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ExpenseRecord(BaseModel):
    expense_id: str
    employee_id: str
    amount: float
    currency: str = "INR"
    category: str
    description: str
    status: ExpenseStatus
    approver_id: Optional[str] = None
    created_at: Optional[str] = None

class ERPExecutionResponse(BaseModel):
    success: bool
    action_type: str
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
