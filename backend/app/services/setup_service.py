from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.models.org import CompanySettings, LeaveType
from app.core.security import hash_password
from app.db.init_db import DEFAULT_LEAVE_TYPES


def setup_completed(db: Session) -> bool:
    return db.query(User).filter(User.role == Role.ADMIN).count() > 0


def first_run_setup(db, company_name, admin_name, admin_email, admin_password) -> User:
    if setup_completed(db):
        raise ValueError("Setup already completed")
    admin = User(email=admin_email.lower(), name=admin_name,
                 password_hash=hash_password(admin_password),
                 role=Role.ADMIN, is_active=True)
    db.add(admin)
    db.add(CompanySettings(company_name=company_name))
    db.commit(); db.refresh(admin)
    # Seed standard leave quotas (Admin can edit via UI)
    if db.query(LeaveType).count() == 0:
        for t in DEFAULT_LEAVE_TYPES:
            db.add(LeaveType(**t))
        db.commit()
    return admin