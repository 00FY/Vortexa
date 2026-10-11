"""backend/schemas/leave.py
Schemas for Leave endpoints.
"""

from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID

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
    status: Optional[LeaveStatus] = None
    rejection_reason: Optional[str] = None


class LeaveResponse(LeaveBase):
    id: Union[UUID, str]
    requester_id: Union[UUID, str]
    status: LeaveStatus
    rejection_reason: Optional[str] = None
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]

    class Config:
        from_attributes = True
        orm_mode = True
