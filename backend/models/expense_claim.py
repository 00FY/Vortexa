import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ExpenseCategory(str):
    TRAVEL = "travel"
    FOOD = "food"
    EQUIPMENT = "equipment"
    ACCOMMODATION = "accommodation"
    OTHER = "other"


class ExpenseStatus(str):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


expense_category_enum = Enum(
    ExpenseCategory.TRAVEL,
    ExpenseCategory.FOOD,
    ExpenseCategory.EQUIPMENT,
    ExpenseCategory.ACCOMMODATION,
    ExpenseCategory.OTHER,
    name="expense_category",
    native_enum=True,
)

expense_status_enum = Enum(
    ExpenseStatus.PENDING,
    ExpenseStatus.APPROVED,
    ExpenseStatus.REJECTED,
    ExpenseStatus.PAID,
    name="expense_status",
    native_enum=True,
)


class ExpenseClaim(Base):
    __tablename__ = "expense_claims"

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
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    category = Column(expense_category_enum, nullable=False)
    description = Column(Text, nullable=True)
    expense_date = Column(Date, nullable=False)
    status = Column(
        expense_status_enum,
        nullable=False,
        default=ExpenseStatus.PENDING,
    )
    rejection_reason = Column(Text, nullable=True)
    payment_reference_id = Column(UUID(as_uuid=True), nullable=True)
    payment_date = Column(Date, nullable=True)
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
        return f"<ExpenseClaim(id={self.id}, status={self.status!r})>"