"""backend/schemas/leave.py
Schemas for Leave endpoints.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field
from models.leave_request import LeaveType, LeaveStatus

class LeaveBase(BaseModel):
    leave_type: LeaveType = Field(..., example=LeaveType.ANNUAL)
    start_date: date = Field(..., example="2023-07-01")
    end_date: date = Field(..., example="2023-07-05")
    reason: Optional[str] = Field(None, example="Family vacation")

class LeaveCreate(LeaveBase):
    pass

class LeaveUpdate(BaseModel):
    status: Optional[LeaveStatus]
    rejection_reason: Optional[str]

class LeaveResponse(LeaveBase):
    id: str
    requester_id: str
    status: LeaveStatus
    rejection_reason: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        orm_state = True
