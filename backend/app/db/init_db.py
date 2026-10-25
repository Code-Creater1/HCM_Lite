from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.user import User, Role
from app.models.org import CompanySettings, LeaveType
from app.models.employee import Employee
from app.models.audit import AuditLog
from app.models.attendance import Attendance, AttendanceCorrection
from app.models.leave import LeaveRequest
from app.core.security import hash_password


DEFAULT_LEAVE_TYPES = [
    {"name": "Annual", "code": "AL", "yearly_quota": 14, "is_paid": True},
    {"name": "Sick",   "code": "SL", "yearly_quota": 8,  "is_paid": True},
    {"name": "Casual", "code": "CL", "yearly_quota": 10, "is_paid": True},
    {"name": "Unpaid", "code": "UL", "yearly_quota": 0,  "is_paid": False},
]


def _seed_leave_types_if_admin_exists(db):
    if db.query(User).filter(User.role == Role.ADMIN).count() > 0 \
            and db.query(LeaveType).count() == 0:
        for t in DEFAULT_LEAVE_TYPES:
            db.add(LeaveType(**t))
        db.commit()


def init_db():
    Base.metadata.create_all(bind=engine)
    if settings.admin_email and settings.admin_password:
        db = SessionLocal()
        try:
            if db.query(User).filter(User.role == Role.ADMIN).count() == 0:
                db.add(User(email=settings.admin_email.lower(),
                            name=settings.admin_name,
                            password_hash=hash_password(settings.admin_password),
                            role=Role.ADMIN, is_active=True))
                db.add(CompanySettings(company_name=settings.company_name_default))
                db.commit()
            _seed_leave_types_if_admin_exists(db)
        finally:
            db.close()
    else:
        # ensure existing installs (setup done earlier) also get leave types
        db = SessionLocal()
        try: _seed_leave_types_if_admin_exists(db)
        finally: db.close()