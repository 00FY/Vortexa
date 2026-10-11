# backend/routers/employee.py
"""Employee CRUD API with role‑based access and audit logging.

Endpoints:
* GET /               – list employees (filters optional)
* GET /{employee_id}   – employee detail
* POST /               – create (admin only)
* PATCH /{employee_id} – update (admin only)
* DELETE /{employee_id} – soft‑delete (admin only)
* POST /{employee_id}/toggle_status – toggle active flag (admin only)
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.dependencies import get_current_user, require_role
from core.database import get_db
from core.security import hash_password
from models import Employee, User, ActivityLog, ActorType, PolicyCheckPath
from services.policy_hook import policy_check
from schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse

router = APIRouter()

# Helper to map SQLAlchemy model to Pydantic response (orm_mode)
def _to_response(emp: Employee) -> EmployeeResponse:
    return EmployeeResponse.from_orm(emp)

@router.get("/", response_model=list[EmployeeResponse])
def list_employees(
    department: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Admin sees everything
    if current_user.role == "admin":
        query = db.query(Employee)
    # Manager sees own record + direct reports
    elif current_user.role == "manager":
        manager_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not manager_emp:
            raise HTTPException(status_code=404, detail="Manager profile not found")
        query = db.query(Employee).filter(
            (Employee.manager_id == manager_emp.id) | (Employee.user_id == current_user.id)
        )
    # Employee sees only self
    else:
        query = db.query(Employee).filter(Employee.user_id == current_user.id)

    if department:
        query = query.filter(Employee.department == department)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    return [_to_response(e) for e in query.all()]

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp = db.get(Employee, employee_id)
    if not emp or emp.deleted_at:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Permission checks – same logic as list
    if current_user.role == "admin":
        pass
    elif current_user.role == "manager":
        manager_emp = db.query(Employee).filter(Employee.user_id == current_user.id).first()
        if not (emp.manager_id == manager_emp.id or emp.user_id == current_user.id):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    else:  # employee
        if emp.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    return _to_response(emp)

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    # Ensure email uniqueness via linked user
    # For demo, we assume a user already exists and is linked via manager_id if provided.
    # In a real system we would also create a User record.
    # Here we just create the Employee record.
    employee = Employee(
        full_name=payload.full_name,
        department=payload.department,
        designation=payload.designation,
        phone=payload.phone,
        employee_code=payload.employee_code,
        date_of_joining=payload.date_of_joining,
        manager_id=payload.manager_id,
    )
    db.add(employee)
    db.flush()  # obtain PK before logging

    # Policy hook
    policy_check(
        actor=_.id,
        action="create_employee",
        resource="Employee",
        resource_id=str(employee.id),
        params=payload.dict(),
    )

    # Audit log – after state only for creation
    log = ActivityLog(
        actor_id=_.id,
        actor_type=ActorType.USER,
        action="create_employee",
        resource="Employee",
        resource_id=employee.id,
        after_state={"id": str(employee.id), **payload.dict()},
        request_id=employee.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(employee)
    return _to_response(employee)

@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    emp = db.get(Employee, employee_id)
    if not emp or emp.deleted_at:
        raise HTTPException(status_code=404, detail="Employee not found")
    before = {"full_name": emp.full_name, "department": emp.department, "designation": emp.designation,
              "phone": emp.phone, "employee_code": emp.employee_code, "date_of_joining": str(emp.date_of_joining),
              "manager_id": str(emp.manager_id) if emp.manager_id else None, "is_active": emp.is_active}

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(emp, field, value)
    db.flush()

    # Policy hook
    policy_check(
        actor=current_user.id,
        action="update_employee",
        resource="Employee",
        resource_id=str(emp.id),
        params=payload.dict(exclude_unset=True),
    )

    # Audit log
    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="update_employee",
        resource="Employee",
        resource_id=emp.id,
        before_state=before,
        after_state={"full_name": emp.full_name, "department": emp.department,
                      "designation": emp.designation, "phone": emp.phone,
                      "employee_code": emp.employee_code,
                      "date_of_joining": str(emp.date_of_joining),
                      "manager_id": str(emp.manager_id) if emp.manager_id else None,
                      "is_active": emp.is_active},
        request_id=emp.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(emp)
    return _to_response(emp)

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    emp = db.get(Employee, employee_id)
    if not emp or emp.deleted_at:
        raise HTTPException(status_code=404, detail="Employee not found")
    before = {"is_active": emp.is_active, "deleted_at": emp.deleted_at}
    emp.is_active = False
    emp.deleted_at = datetime.now(timezone.utc)
    db.flush()

    policy_check(
        actor=current_user.id,
        action="soft_delete_employee",
        resource="Employee",
        resource_id=str(emp.id),
        params={},
    )

    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="soft_delete_employee",
        resource="Employee",
        resource_id=emp.id,
        before_state=before,
        after_state={"is_active": emp.is_active, "deleted_at": str(emp.deleted_at)},
        request_id=emp.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    return

@router.post("/{employee_id}/toggle_status", response_model=EmployeeResponse)
def toggle_employee_status(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    emp = db.get(Employee, employee_id)
    if not emp or emp.deleted_at:
        raise HTTPException(status_code=404, detail="Employee not found")
    before = {"is_active": emp.is_active}
    emp.is_active = not emp.is_active
    db.flush()

    policy_check(
        actor=current_user.id,
        action="toggle_employee_status",
        resource="Employee",
        resource_id=str(emp.id),
        params={"new_status": emp.is_active},
    )

    log = ActivityLog(
        actor_id=current_user.id,
        actor_type=ActorType.USER,
        action="toggle_employee_status",
        resource="Employee",
        resource_id=emp.id,
        before_state=before,
        after_state={"is_active": emp.is_active},
        request_id=emp.id,
        policy_check_path=PolicyCheckPath.RULES_ONLY,
    )
    db.add(log)
    db.commit()
    db.refresh(emp)
    return _to_response(emp)
