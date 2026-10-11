import os
import uuid
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, engine
from core.security import hash_password
from models import (
    User,
    UserRole,
    Employee,
    Department,
    LeaveRequest,
    LeaveType,
    LeaveStatus,
    ExpenseClaim,
    ExpenseCategory,
    ExpenseStatus,
    ActivityLog,
)

SessionLocal = sessionmaker(bind=engine)


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Admin
    admin = db.query(User).filter(User.email == "admin@novapay.com").first()
    if not admin:
        admin = User(
            id=uuid.uuid4(),
            email="admin@novapay.com",
            hashed_password=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.flush()

        admin_emp = Employee(
            id=uuid.uuid4(),
            user_id=admin.id,
            full_name="Admin User",
            department=Department.OPERATIONS,
            designation="System Administrator",
            employee_code="ADM001",
            date_of_joining=date(2023, 1, 1),
            is_active=True,
        )
        db.add(admin_emp)

    # Manager
    manager = db.query(User).filter(User.email == "manager@example.com").first()
    if not manager:
        manager = User(
            id=uuid.uuid4(),
            email="manager@example.com",
            hashed_password=hash_password("manager123"),
            role=UserRole.MANAGER,
            is_active=True,
        )
        db.add(manager)
        db.flush()

        manager_emp = Employee(
            id=uuid.uuid4(),
            user_id=manager.id,
            full_name="Jane Manager",
            department=Department.ENGINEERING,
            designation="Engineering Manager",
            employee_code="MGR001",
            date_of_joining=date(2023, 2, 1),
            is_active=True,
        )
        db.add(manager_emp)

    # Employee
    employee = db.query(User).filter(User.email == "employee@example.com").first()
    if not employee:
        employee = User(
            id=uuid.uuid4(),
            email="employee@example.com",
            hashed_password=hash_password("employee123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        db.add(employee)
        db.flush()

        mgr = db.query(Employee).filter(Employee.employee_code == "MGR001").first()
        emp_profile = Employee(
            id=uuid.uuid4(),
            user_id=employee.id,
            full_name="John Doe",
            department=Department.ENGINEERING,
            designation="Software Engineer",
            employee_code="EMP001",
            date_of_joining=date(2023, 3, 1),
            manager_id=mgr.id if mgr else None,
            is_active=True,
        )
        db.add(emp_profile)

    db.commit()
    print("Database seeding completed successfully.")
    db.close()


if __name__ == "__main__":
    seed()
