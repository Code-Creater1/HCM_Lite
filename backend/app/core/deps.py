from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User, Role

bearer = HTTPBearer(auto_error=False)

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not creds: raise HTTPException(401, "Not authenticated")
    try: payload = decode_token(creds.credentials)
    except JWTError: raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active: raise HTTPException(401, "Inactive or unknown user")
    return user

def require_roles(*roles: Role):
    def guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(403, f"Forbidden — requires one of {[r.value for r in roles]}")
        return user
    return guard

def require_password_changed(user: User = Depends(get_current_user)) -> User:
    if user.must_change_password:
        raise HTTPException(403, "You must change your password before using this endpoint")
    return user