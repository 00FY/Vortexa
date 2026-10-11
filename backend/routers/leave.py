# backend/routers/leave.py
"""Leave request API with role‑based access, state machine enforcement, policy checks, and audit logging.

Endpoints:
* POST   /               – submit a new leave request (employee only)
* GET    /my             – list own leave history (employee)
* GET    /pending        – list pending requests (manager sees direct reports, admin sees all)
* GET    /{leave_id}     – view a specific request (allowed if requester, manager of requester, or admin)
* PATCH  /{leave_id}/approve   – approve (manager or admin, not self)
* PATCH  /{leave_id}/reject    – reject with reason (manager or admin, not self)
* PATCH  /{leave_id}/cancel    – cancel by requester (still pending)
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_role
from core.database import get_db
from services.policy_hook import policy_check
from models import (
    LeaveRequest,
    Employee,
    ActivityLog,
    ActorType,
    PolicyCheckPath,
    LeaveStatus,
)
from schemas.leave import LeaveCreate, LeaveUpdate, LeaveResponse

router = APIRouter()

def _to_response(lr: LeaveRequest) -> LeaveResponse:
    return LeaveResponse.from_orm(lr)

# --------------------------------------------------------------------- #
# Helper: fetch employee profile for current user
# --------------------------------------------------------------------- #
def _get_employee(db: Session, user_id: str) -> Employee:
    emp = db.query(Employee).filter(Employee.user_id == user_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return emp

# --------------------------------------------------------------------- #
# Submit a leave request – employee only
# --------------------------------------------------------------------- #
@router.post("/", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
def submit_leave(
    payload: LeaveCreate,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(require_role("employee")),
):
    requester = _get_employee(db, current_user.id)
    leave = LeaveRequest(
        requester_id=requester.id,
        leave_type=payload.leave_type,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
        status=LeaveStatus.PENDING,
    )
    db.add(leave)
    db.flush()

    # Policy hook
    policy_check(
        actor=current_user.id,
        action="submit_leave",
        resource="LeaveRequest",
        resource_id=str(leave.id),
        params=payload.dict(),
    )

    # Audit – after state only for creation
    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="submit_leave",
        resource="LeaveRequest",
        resource_id=leave.id,
        after_state={"id": str(leave.id), **payload.dict()},
        request_id=leave.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(leave)
    return _to_response(leave)

# --------------------------------------------------------------------- #
# List own leave history
# --------------------------------------------------------------------- #
@router.get("/my", response_model=list[LeaveResponse])
def list_my_leaves(
    db: Session = Depends(get_db),
    current_user: "User" = Depends(require_role("employee")),
):
    employee = _get_employee(db, current_user.id)
    leaves = db.query(LeaveRequest).filter(LeaveRequest.requester_id == employee.id).all()
    return [_to_response(l) for l in leaves]

# --------------------------------------------------------------------- #
# List pending requests – manager sees direct reports, admin sees all
# --------------------------------------------------------------------- #
@router.get("/pending", response_model=list[LeaveResponse])
def list_pending(
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    if current_user.role == "admin":
        query = db.query(LeaveRequest).filter(LeaveRequest.status == LeaveStatus.PENDING)
    elif current_user.role == "manager":
        manager_emp = _get_employee(db, current_user.id)
        # direct reports are employees where manager_id == manager_emp.id
        direct_ids = (
            db.query(Employee.id)
            .filter(Employee.manager_id == manager_emp.id)
            .subquery()
        )
        query = db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.PENDING,
            LeaveRequest.requester_id.in_(direct_ids),
        )
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return [_to_response(l) for l in query.all()]

# --------------------------------------------------------------------- #
# Get a specific leave request – allowed for requester, manager of requester, admin
# --------------------------------------------------------------------- #
@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(
    leave_id: str,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(get_current_user),
):
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    # permission check
    if current_user.role == "admin":
        pass
    elif current_user.role == "manager":
        manager_emp = _get_employee(db, current_user.id)
        if leave.requester.manager_id != manager_emp.id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    else:  # employee
        emp = _get_employee(db, current_user.id)
        if leave.requester_id != emp.id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return _to_response(leave)

# --------------------------------------------------------------------- #
# Approve leave – manager or admin, cannot approve own request
# --------------------------------------------------------------------- #
@router.patch("/{leave_id}/approve", response_model=LeaveResponse)
def approve_leave(
    leave_id: str,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(require_role("manager", "admin")),
):
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(status_code=400, detail="Leave not in pending state")
    # prevent self‑approval
    employee = db.get(Employee, leave.requester_id)
    if employee.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot approve own request")
    # manager can only approve direct reports
    if current_user.role == "manager":
        manager_emp = _get_employee(db, current_user.id)
        if employee.manager_id != manager_emp.id:
            raise HTTPException(status_code=403, detail="Can only approve direct reports")
    before = {"status": leave.status}
    leave.status = LeaveStatus.APPROVED
    leave.reviewed_by = db.query(Employee).filter(Employee.user_id == current_user.id).first().id
    db.flush()

    policy_check(
        actor=current_user.id,
        action="approve_leave",
        resource="LeaveRequest",
        resource_id=str(leave.id),
        params={},
    )

    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="approve_leave",
        resource="LeaveRequest",
        resource_id=leave.id,
        before_state=before,
        after_state={"status": leave.status},
        request_id=leave.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(leave)
    return _to_response(leave)

# --------------------------------------------------------------------- #
# Reject leave – manager or admin, requires reason, same restrictions as approve
# --------------------------------------------------------------------- #
@router.patch("/{leave_id}/reject", response_model=LeaveResponse)
def reject_leave(
    leave_id: str,
    payload: LeaveUpdate,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(require_role("manager", "admin")),
):
    if not payload.rejection_reason:
        raise HTTPException(status_code=400, detail="Rejection reason required")
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(status_code=400, detail="Leave not in pending state")
    employee = db.get(Employee, leave.requester_id)
    if employee.user_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot reject own request")
    if current_user.role == "manager":
        manager_emp = _get_employee(db, current_user.id)
        if employee.manager_id != manager_emp.id:
            raise HTTPException(status_code=403, detail="Can only reject direct reports")
    before = {"status": leave.status, "rejection_reason": leave.rejection_reason}
    leave.status = LeaveStatus.REJECTED
    leave.rejection_reason = payload.rejection_reason
    leave.reviewed_by = db.query(Employee).filter(Employee.user_id == current_user.id).first().id
    db.flush()

    policy_check(
        actor=current_user.id,
        action="reject_leave",
        resource="LeaveRequest",
        resource_id=str(leave.id),
        params={"rejection_reason": payload.rejection_reason},
    )

    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="reject_leave",
        resource="LeaveRequest",
        resource_id=leave.id,
        before_state=before,
        after_state={"status": leave.status, "rejection_reason": leave.rejection_reason},
        request_id=leave.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(leave)
    return _to_response(leave)

# --------------------------------------------------------------------- #
# Cancel leave – requester only while pending
# --------------------------------------------------------------------- #
@router.patch("/{leave_id}/cancel", response_model=LeaveResponse)
def cancel_leave(
    leave_id: str,
    db: Session = Depends(get_db),
    current_user: "User" = Depends(require_role("employee")),
):
    employee = _get_employee(db, current_user.id)
    leave = db.get(LeaveRequest, leave_id)
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if leave.requester_id != employee.id:
        raise HTTPException(status_code=403, detail="Can only cancel own request")
    if leave.status != LeaveStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending leaves can be cancelled")
    before = {"status": leave.status}
    leave.status = LeaveStatus.CANCELLED
    db.flush()

    policy_check(
        actor=current_user.id,
        action="cancel_leave",
        resource="LeaveRequest",
        resource_id=str(leave.id),
        params={},
    )

    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="cancel_leave",
        resource="LeaveRequest",
        resource_id=leave.id,
        before_state=before,
        after_state={"status": leave.status},
        request_id=leave.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(leave)
    return _to_response(leave)
