from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from app.db.session import get_db
from app.core.deps import require_roles, require_password_changed
from app.models.user import User, Role
from app.models.employee import Employee
from app.schemas.attendance import CorrectionIn, CorrectionReviewIn
from app.services import attendance_service, employee_service, audit_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _emp_id(db, user) -> int:
    e = employee_service.get_self(db, user.id)
    if not e: raise HTTPException(404, "Employee profile not found")
    return e.id


# ---------- Employee ----------
@router.post("/check-in")
def check_in(db: Session = Depends(get_db),
             user: User = Depends(require_roles(Role.EMPLOYEE)),
             _: User = Depends(require_password_changed)):
    try:
        a = attendance_service.check_in(db, _emp_id(db, user))
    except ValueError as e:
        raise HTTPException(409 if "Already" in str(e) else 400, str(e))
    audit_service.log(db, user.id, "CHECK_IN", "attendance", a.id)
    return {"id": a.id, "check_in": a.check_in, "status": a.status}


@router.post("/check-out")
def check_out(db: Session = Depends(get_db),
              user: User = Depends(require_roles(Role.EMPLOYEE)),
              _: User = Depends(require_password_changed)):
    try:
        a = attendance_service.check_out(db, _emp_id(db, user))
    except ValueError as e:
        raise HTTPException(400, str(e))
    audit_service.log(db, user.id, "CHECK_OUT", "attendance", a.id)
    return {"id": a.id, "check_out": a.check_out,
            "status": a.status, "worked_minutes": a.worked_minutes}


@router.get("/me/today")
def today(db: Session = Depends(get_db),
          user: User = Depends(require_roles(Role.EMPLOYEE)),
          _: User = Depends(require_password_changed)):
    a = attendance_service.today_record(db, _emp_id(db, user))
    if not a: return {"exists": False}
    return {"exists": True, "id": a.id,
            "check_in": a.check_in, "check_out": a.check_out,
            "status": a.status, "worked_minutes": a.worked_minutes}


@router.get("/me/calendar")
def my_calendar(year: int, month: int, db: Session = Depends(get_db),
                user: User = Depends(require_roles(Role.EMPLOYEE)),
                _: User = Depends(require_password_changed)):
    return attendance_service.calendar(db, _emp_id(db, user), year, month)


@router.post("/corrections")
def request_correction(payload: CorrectionIn, db: Session = Depends(get_db),
                       user: User = Depends(require_roles(Role.EMPLOYEE)),
                       _: User = Depends(require_password_changed)):
    try:
        c = attendance_service.request_correction(
            db, _emp_id(db, user), payload.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
    audit_service.log(db, user.id, "REQUEST_CORRECTION", "correction", c.id)
    return {"id": c.id, "status": c.status}


@router.get("/corrections/me")
def my_corrections(db: Session = Depends(get_db),
                   user: User = Depends(require_roles(Role.EMPLOYEE)),
                   _: User = Depends(require_password_changed)):
    return [{"id": c.id, "date": c.date, "reason": c.reason,
             "requested_check_in": c.requested_check_in,
             "requested_check_out": c.requested_check_out,
             "status": c.status, "review_comment": c.review_comment}
            for c in attendance_service.list_corrections(db, employee_id=_emp_id(db, user))]


# ---------- HR / Admin ----------
@router.get("/board")
def board(date_str: str = Query(None, alias="date"), db: Session = Depends(get_db),
          _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    d = date.fromisoformat(date_str) if date_str else date.today()
    return attendance_service.daily_board(db, d)


@router.get("/corrections")
def all_corrections(status: str = None, db: Session = Depends(get_db),
                    _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    out = []
    for c in attendance_service.list_corrections(db, status=status):
        e = db.get(Employee, c.employee_id)
        out.append({
            "id": c.id, "employee_id": c.employee_id,
            "employee_name": e.user.name if e and e.user else None,
            "date": c.date,
            "requested_check_in": c.requested_check_in,
            "requested_check_out": c.requested_check_out,
            "reason": c.reason, "status": c.status,
            "created_at": c.created_at,
        })
    return out


@router.post("/corrections/{cid}/review")
def review_correction(cid: int, payload: CorrectionReviewIn,
                      db: Session = Depends(get_db),
                      reviewer: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    if payload.action not in ("approve", "reject"):
        raise HTTPException(400, "action must be 'approve' or 'reject'")
    try:
        c = attendance_service.review_correction(
            db, cid, reviewer.id, payload.action, payload.comment)
    except LookupError as e: raise HTTPException(404, str(e))
    except ValueError as e: raise HTTPException(400, str(e))
    audit_service.log(db, reviewer.id, payload.action.upper(), "correction", c.id)
    return {"id": c.id, "status": c.status}