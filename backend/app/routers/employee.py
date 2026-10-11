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

@router.post('/', response_model=schemas.EmployeeRead)
def create_employee(emp_in: schemas.EmployeeCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.RoleEnum.ADMIN, models.RoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail='Insufficient permissions')
    employee = models.Employee(**emp_in.dict())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@router.get('/', response_model=List[schemas.EmployeeRead])
def list_employees(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role not in [models.RoleEnum.ADMIN, models.RoleEnum.MANAGER]:
        raise HTTPException(status_code=403, detail='Insufficient permissions')
    return db.query(models.Employee).offset(skip).limit(limit).all()
