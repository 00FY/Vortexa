from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from .. import models, dependencies, auth

router = APIRouter()

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(dependencies.get_db)):
    payload = auth.decode_token(token)
    user = db.query(models.User).filter(models.User.id == int(payload.get('sub'))).first()
    if not user:
        raise HTTPException(status_code=401, detail='Invalid authentication')
    return user

@router.get('/stats', response_model=Dict[str, int])
def get_stats(db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.RoleEnum.ADMIN, models.RoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail='Insufficient permissions')
    employee_count = db.query(models.Employee).count()
    pending_leaves = db.query(models.LeaveRequest).filter(models.LeaveRequest.status == models.LeaveStatus.PENDING).count()
    pending_expenses = db.query(models.ExpenseClaim).filter(models.ExpenseClaim.status == models.ExpenseStatus.PENDING).count()
    return {'employees': employee_count, 'pending_leaves': pending_leaves, 'pending_expenses': pending_expenses}
