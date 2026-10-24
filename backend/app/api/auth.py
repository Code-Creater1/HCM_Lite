from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginIn, TokenOut, ChangePasswordIn
from app.services import auth_service
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    u = auth_service.authenticate(db, payload.email, payload.password)
    if not u: raise HTTPException(401, "Invalid email or password")
    return auth_service.token_response(u)

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name,
            "role": user.role.value, "must_change_password": user.must_change_password}

@router.post("/change-password")
def change_password(payload: ChangePasswordIn, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user)):
    if not auth_service.change_password(db, user, payload.current_password, payload.new_password):
        raise HTTPException(400, "Current password is incorrect")
    return {"status": "ok"}