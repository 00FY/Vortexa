from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship, declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.EMPLOYEE, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    full_name = Column(String, nullable=False)
    position = Column(String)
    department = Column(String)
    is_active = Column(Boolean, default=True)
    user = relationship('User')

class LeaveStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    reason = Column(String)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship('Employee')

class ExpenseStatus(str, enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class ExpenseClaim(Base):
    __tablename__ = 'expense_claims'
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String)
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    payment_reference = Column(String, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    employee = relationship('Employee')

class ActivityLog(Base):
    __tablename__ = 'activity_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship('User')
