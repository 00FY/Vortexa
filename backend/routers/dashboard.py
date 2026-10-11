from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from models import Employee, ExpenseClaim, ExpenseStatus, LeaveRequest, LeaveStatus, User, UserRole

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=Dict[str, int])
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER, "admin", "manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    employee_count = db.query(Employee).filter(Employee.deleted_at == None).count()
    pending_leaves = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.PENDING).count()
    pending_expenses = db.query(ExpenseClaim).filter(ExpenseClaim.status == ExpenseStatus.PENDING).count()
    return {
        "employees": employee_count,
        "pending_leaves": pending_leaves,
        "pending_expenses": pending_expenses,
    }
