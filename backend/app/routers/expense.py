from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, dependencies, auth

router = APIRouter()

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(dependencies.get_db)):
    payload = auth.decode_token(token)
    user = db.query(models.User).filter(models.User.id == int(payload.get('sub'))).first()
    if not user:
        raise HTTPException(status_code=401, detail='Invalid authentication')
    return user

@router.post('/', response_model=schemas.ExpenseClaimRead)
def submit_expense(req: schemas.ExpenseClaimCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role != models.RoleEnum.EMPLOYEE:
        raise HTTPException(status_code=403, detail='Only employees can submit expenses')
    employee = db.query(models.Employee).filter(models.Employee.user_id == current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail='Employee profile not found')
    claim = models.ExpenseClaim(employee_id=employee.id, **req.dict())
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim

@router.patch('/{claim_id}', response_model=schemas.ExpenseClaimRead)
def review_expense(claim_id: int, status: models.ExpenseStatus, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.RoleEnum.MANAGER, models.RoleEnum.ADMIN]:
        raise HTTPException(status_code=403, detail='Insufficient permissions')
    claim = db.query(models.ExpenseClaim).filter(models.ExpenseClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail='Expense claim not found')
    claim.status = status
    db.commit()
    db.refresh(claim)
    return claim
