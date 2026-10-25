from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.core.security import hash_password

def create_hr_login(db: Session, name, email, temp_password) -> User:
    if db.query(User).filter(User.email == email.lower()).first():
        raise ValueError("Email already in use")
    u = User(email=email.lower(), name=name,
             password_hash=hash_password(temp_password),
             role=Role.HR, is_active=True, must_change_password=True)
    db.add(u); db.commit(); db.refresh(u)
    return u

def list_hr_logins(db: Session):
    return db.query(User).filter(User.role.in_([Role.HR, Role.ADMIN])).all()

def deactivate(db, user_id) -> bool:
    u = db.get(User, user_id)
    if not u or u.role == Role.ADMIN: return False
    u.is_active = False; db.commit(); return True

def reset_password(db, user_id, new_password) -> bool:
    u = db.get(User, user_id)
    if not u: return False
    u.password_hash = hash_password(new_password)
    u.must_change_password = True
    db.commit(); return True