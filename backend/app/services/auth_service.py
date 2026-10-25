from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import verify_password, hash_password, create_token

def authenticate(db: Session, email: str, password: str):
    u = db.query(User).filter(User.email == email.lower()).first()
    if not u or not u.is_active or not verify_password(password, u.password_hash):
        return None
    return u

def token_response(u: User):
    return {"access_token": create_token(u.id, u.role.value), "token_type": "bearer",
            "role": u.role, "name": u.name, "must_change_password": u.must_change_password}

def change_password(db: Session, user: User, current: str, new: str) -> bool:
    if not verify_password(current, user.password_hash): return False
    user.password_hash = hash_password(new)
    user.must_change_password = False
    db.commit(); return True