from datetime import date
from sqlalchemy.orm import Session

from app.models.leave import LeaveRequest
from app.models.org import LeaveType
from app.utils.dates import working_days_list


def list_leave_types(db: Session):
    return db.query(LeaveType).all()


def balance(db: Session, employee_id: int, year: int = None) -> list:
    year = year or date.today().year
    start, end = date(year, 1, 1), date(year, 12, 31)
    approved = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status == "approved",
        LeaveRequest.start_date >= start,
        LeaveRequest.end_date <= end).all()
    used = {}
    for lv in approved:
        used[lv.leave_type_id] = used.get(lv.leave_type_id, 0) + lv.days
    out = []
    for t in db.query(LeaveType).all():
        u = used.get(t.id, 0)
        out.append({
            "leave_type_id": t.id, "name": t.name, "code": t.code,
            "quota": t.yearly_quota, "used": u,
            "remaining": None if t.yearly_quota == 0 else max(0, t.yearly_quota - u),
            "is_paid": t.is_paid,
        })
    return out


def apply(db: Session, employee_id: int, data: dict) -> LeaveRequest:
    lt = db.get(LeaveType, data["leave_type_id"])
    if not lt: raise ValueError("Leave type not found")
    start, end = data["start_date"], data["end_date"]
    if end < start: raise ValueError("End date must be on or after start date")
    days = working_days_list(db, start, end)
    if not days:
        raise ValueError("Range contains no working days (weekend/holiday only)")
    n = len(days)
    # Overlap
    ov = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.status.in_(["pending", "approved"]),
        LeaveRequest.start_date <= end,
        LeaveRequest.end_date >= start).first()
    if ov: raise ValueError("Overlaps with an existing pending/approved leave")
    # Balance
    if lt.yearly_quota > 0:
        for b in balance(db, employee_id, year=start.year):
            if b["leave_type_id"] == lt.id and b["remaining"] is not None:
                if n > b["remaining"]:
                    raise ValueError(f"Insufficient balance: requested {n}, remaining {b['remaining']}")
    lv = LeaveRequest(employee_id=employee_id, leave_type_id=lt.id,
                      start_date=start, end_date=end, days=n,
                      reason=data["reason"], status="pending")
    db.add(lv); db.commit(); db.refresh(lv); return lv


def cancel(db: Session, employee_id: int, leave_id: int) -> LeaveRequest:
    lv = db.get(LeaveRequest, leave_id)
    if not lv or lv.employee_id != employee_id:
        raise LookupError("Leave not found")
    if lv.status not in ("pending", "approved"):
        raise ValueError("Cannot cancel this leave")
    lv.status = "cancelled"
    db.commit(); db.refresh(lv); return lv


def list_my(db: Session, employee_id: int):
    return db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id
    ).order_by(LeaveRequest.created_at.desc()).all()


def review(db: Session, leave_id: int, reviewer_id: int,
           action: str, comment: str | None) -> LeaveRequest:
    lv = db.get(LeaveRequest, leave_id)
    if not lv: raise LookupError("Leave not found")
    if lv.status != "pending": raise ValueError("Already reviewed")
    lv.status = "approved" if action == "approve" else "rejected"
    lv.reviewed_by_id = reviewer_id
    lv.review_comment = comment
    db.commit(); db.refresh(lv); return lv