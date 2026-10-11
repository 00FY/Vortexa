import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

import enum
from core.database import Base


class LeaveType(str, enum.Enum):
    CASUAL = "casual"
    SICK = "sick"
    ANNUAL = "annual"
    UNPAID = "unpaid"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


leave_type_enum = Enum(
    LeaveType,
    name="leave_type",
    native_enum=True,
)

leave_status_enum = Enum(
    LeaveStatus,
    name="leave_status",
    native_enum=True,
)


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )
    leave_type = Column(leave_type_enum, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=True)
    status = Column(leave_status_enum, nullable=False, default=LeaveStatus.PENDING)
    rejection_reason = Column(Text, nullable=True)
    request_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    requester = relationship("Employee", foreign_keys=[requester_id])
    reviewer = relationship("Employee", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, status={self.status!r})>"