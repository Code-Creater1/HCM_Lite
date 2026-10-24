from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require_roles
from app.models.user import User, Role
from app.schemas.employee import HRLoginCreateIn
from app.services import user_service, audit_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/hr")
def list_hr(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN))):
    return [{"id": u.id, "name": u.name, "email": u.email,
             "role": u.role.value, "is_active": u.is_active}
            for u in user_service.list_hr_logins(db)]

@router.post("/hr", status_code=201)
def create_hr(payload: HRLoginCreateIn, db: Session = Depends(get_db),
              admin: User = Depends(require_roles(Role.ADMIN))):
    try:
        u = user_service.create_hr_login(db, payload.name, payload.email, payload.temporary_password)
    except ValueError as e:
        raise HTTPException(409, str(e))
    audit_service.log(db, admin.id, "CREATE", "user", u.id, after={"email": u.email, "role": "HR"})
    return {"id": u.id, "email": u.email, "name": u.name}

@router.post("/{user_id}/deactivate")
def deactivate(user_id: int, db: Session = Depends(get_db),
               admin: User = Depends(require_roles(Role.ADMIN))):
    if not user_service.deactivate(db, user_id):
        raise HTTPException(400, "Cannot deactivate this user")
    audit_service.log(db, admin.id, "DEACTIVATE", "user", user_id)
    return {"status": "ok"}

@router.post("/{user_id}/reset-password")
def reset(user_id: int, payload: dict, db: Session = Depends(get_db),
          admin: User = Depends(require_roles(Role.ADMIN))):
    pw = payload.get("new_password", "")
    if len(pw) < 8: raise HTTPException(400, "Password must be at least 8 chars")
    if not user_service.reset_password(db, user_id, pw):
        raise HTTPException(404, "User not found")
    audit_service.log(db, admin.id, "RESET_PASSWORD", "user", user_id)
    return {"status": "ok"}