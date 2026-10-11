"""Register all models so SQLAlchemy/Alembic can discover them.

Importing this module ensures every model is imported and attached to the
declarative Base before Alembic inspects the metadata.
"""

from models.activity_log import ActivityLog, ActorType, PolicyCheckPath
from models.employee import Department, Employee
from models.expense_claim import ExpenseClaim, ExpenseCategory, ExpenseStatus
from models.leave_request import LeaveRequest, LeaveStatus, LeaveType
from models.user import User, UserRole

__all__ = [
    "ActivityLog",
    "ActorType",
    "PolicyCheckPath",
    "Department",
    "Employee",
    "ExpenseClaim",
    "ExpenseCategory",
    "ExpenseStatus",
    "LeaveRequest",
    "LeaveStatus",
    "LeaveType",
    "User",
    "UserRole",
]