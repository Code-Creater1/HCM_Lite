from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User, Role
from app.models.org import CompanySettings
from app.models.employee import Employee
from app.models.audit import AuditLog
from app.core.security import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)
    if settings.admin_email and settings.admin_password:
        db = SessionLocal()
        try:
            if db.query(User).filter(User.role == Role.ADMIN).count() == 0:
                db.add(User(email=settings.admin_email.lower(), name=settings.admin_name,
                            password_hash=hash_password(settings.admin_password),
                            role=Role.ADMIN, is_active=True))
                db.add(CompanySettings(company_name=settings.company_name_default))
                db.commit()
        finally: db.close()