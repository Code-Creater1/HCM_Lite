from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require_roles, require_password_changed
from app.models.user import User, Role
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.org import LeaveType
from app.schemas.leave import LeaveApplyIn, LeaveReviewIn
from app.services import leave_service, employee_service, audit_service

router = APIRouter(prefix="/leave", tags=["leave"])


def _emp_id(db, user) -> int:
    e = employee_service.get_self(db, user.id)
    if not e: raise HTTPException(404, "Employee profile not found")
    return e.id


@router.get("/types")
def types(db: Session = Depends(get_db),
          _: User = Depends(require_roles(Role.ADMIN, Role.HR, Role.EMPLOYEE))):
    return [{"id": t.id, "name": t.name, "code": t.code,
             "yearly_quota": t.yearly_quota, "is_paid": t.is_paid}
            for t in leave_service.list_leave_types(db)]


@router.get("/balance/me")
def my_balance(db: Session = Depends(get_db),
               user: User = Depends(require_roles(Role.EMPLOYEE)),
               _: User = Depends(require_password_changed)):
    return leave_service.balance(db, _emp_id(db, user))


@router.get("/balance/{emp_id}")
def emp_balance(emp_id: int, db: Session = Depends(get_db),
                _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    return leave_service.balance(db, emp_id)


@router.post("/apply")
def apply(payload: LeaveApplyIn, db: Session = Depends(get_db),
          user: User = Depends(require_roles(Role.EMPLOYEE)),
          _: User = Depends(require_password_changed)):
    try:
        lv = leave_service.apply(db, _emp_id(db, user), payload.model_dump())
    except ValueError as e:
        raise HTTPException(422, str(e))
    audit_service.log(db, user.id, "APPLY_LEAVE", "leave_request", lv.id)
    return {"id": lv.id, "days": lv.days, "status": lv.status}


@router.post("/{leave_id}/cancel")
def cancel(leave_id: int, db: Session = Depends(get_db),
           user: User = Depends(require_roles(Role.EMPLOYEE)),
           _: User = Depends(require_password_changed)):
    try:
        lv = leave_service.cancel(db, _emp_id(db, user), leave_id)
    except LookupError as e: raise HTTPException(404, str(e))
    except ValueError as e: raise HTTPException(400, str(e))
    audit_service.log(db, user.id, "CANCEL_LEAVE", "leave_request", lv.id)
    return {"id": lv.id, "status": lv.status}


@router.get("/me")
def my_leaves(db: Session = Depends(get_db),
              user: User = Depends(require_roles(Role.EMPLOYEE)),
              _: User = Depends(require_password_changed)):
    return [{"id": lv.id, "leave_type_id": lv.leave_type_id,
             "start_date": lv.start_date, "end_date": lv.end_date,
             "days": lv.days, "reason": lv.reason, "status": lv.status,
             "review_comment": lv.review_comment, "created_at": lv.created_at}
            for lv in leave_service.list_my(db, _emp_id(db, user))]


@router.get("/inbox")
def inbox(status: str = None, db: Session = Depends(get_db),
          _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    q = db.query(LeaveRequest)
    if status: q = q.filter(LeaveRequest.status == status)
    rows = q.order_by(LeaveRequest.created_at.desc()).all()
    lt_map = {t.id: t.name for t in db.query(LeaveType).all()}
    out = []
    for lv in rows:
        e = db.get(Employee, lv.employee_id)
        out.append({
            "id": lv.id, "employee_id": lv.employee_id,
            "employee_name": e.user.name if e and e.user else None,
            "leave_type_id": lv.leave_type_id,
            "leave_type_name": lt_map.get(lv.leave_type_id),
            "start_date": lv.start_date, "end_date": lv.end_date,
            "days": lv.days, "reason": lv.reason, "status": lv.status,
            "review_comment": lv.review_comment, "created_at": lv.created_at,
        })
    return out


@router.post("/{leave_id}/review")
def review(leave_id: int, payload: LeaveReviewIn, db: Session = Depends(get_db),
           reviewer: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    if payload.action not in ("approve", "reject"):
        raise HTTPException(400, "action must be 'approve' or 'reject'")
    try:
        lv = leave_service.review(db, leave_id, reviewer.id, payload.action, payload.comment)
    except LookupError as e: raise HTTPException(404, str(e))
    except ValueError as e: raise HTTPException(400, str(e))
    audit_service.log(db, reviewer.id, payload.action.upper(), "leave_request", lv.id)
    return {"id": lv.id, "status": lv.status}