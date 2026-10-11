from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.dependencies import get_current_user, require_role
from core.security import hash_password, verify_password, create_access_token
from models import User
from schemas.auth import LoginRequest, UserProfileResponse
from models.employee import Employee

router = APIRouter(prefix="/api/auth", tags=["auth"])
users_router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token({"sub": str(user.id)})
    # Set HttpOnly cookie; never return JWT in body per security rule
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.jwt_expiry_minutes * 60,
    )
    # Return only profile (no token in body)
    profile = UserProfileResponse.from_orm(user)
    return profile


@router.post("/token")
@users_router.post("/token")
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Include employee info if linked
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    # Build profile; keep same schema but could extend if needed
    return UserProfileResponse.from_orm(current_user)