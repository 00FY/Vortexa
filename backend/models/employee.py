import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class Department(str):
    ENGINEERING = "Engineering"
    FINANCE = "Finance"
    RISK_COMPLIANCE = "Risk_Compliance"
    OPERATIONS = "Operations"
    HR = "HR"


department_enum = Enum(
    Department.ENGINEERING,
    Department.FINANCE,
    Department.RISK_COMPLIANCE,
    Department.OPERATIONS,
    Department.HR,
    name="department",
    native_enum=True,
)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name = Column(String, nullable=False)
    department = Column(department_enum, nullable=False)
    designation = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    manager_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )
    employee_code = Column(String, unique=True, index=True, nullable=False)
    date_of_joining = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
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

    manager = relationship(
        "Employee",
        remote_side=[id],
        foreign_keys=[manager_id],
        backref="direct_reports",
    )

    def __repr__(self):
        return f"<Employee(id={self.id}, full_name={self.full_name!r})>"