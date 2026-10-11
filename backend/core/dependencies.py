import uuid
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.config import settings
from core.security import decode_access_token
from models import User


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    token = None
    # Check cookie first
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        token = cookie_token
    # Check Authorization header if cookie not present
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    raw_user_id = payload.get("sub")
    if raw_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Support UUID conversion
    try:
        user_id = uuid.UUID(str(raw_user_id)) if not isinstance(raw_user_id, uuid.UUID) else raw_user_id
    except (ValueError, AttributeError):
        user_id = raw_user_id

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


def require_role(*roles):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker