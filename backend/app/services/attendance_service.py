from datetime import datetime, date, time, timedelta
import calendar as _calendar
from sqlalchemy.orm import Session

from app.models.attendance import Attendance, AttendanceCorrection, AttendanceStatus
from app.models.employee import Employee
from app.models.org import CompanySettings
from app.models.leave import LeaveRequest
from app.utils.dates import is_weekend, holidays_set


def _settings(db: Session) -> CompanySettings:
    return db.query(CompanySettings).first()


def _parse_time(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def _grace_cutoff(settings: CompanySettings) -> time:
    start = _parse_time(settings.office_start)
    total = start.hour * 60 + start.minute + settings.grace_minutes
    return time(total // 60, total % 60)


def _compute_status(settings: CompanySettings, check_in: datetime, check_out: datetime | None) -> str:
    if check_out is None:
        return AttendanceStatus.PRESENT.value if check_in.time() <= _grace_cutoff(settings) \
            else AttendanceStatus.LATE.value
    worked = int((check_out - check_in).total_seconds() / 60)
    if worked < settings.half_day_hours * 60:
        return AttendanceStatus.HALF_DAY.value
    return AttendanceStatus.PRESENT.value if check_in.time() <= _grace_cutoff(settings) \
        else AttendanceStatus.LATE.value


def check_in(db: Session, employee_id: int) -> Attendance:
    settings = _settings(db)
    now = datetime.now()
    today = now.date()
    existing = db.query(Attendance).filter(
        Attendance.employee_id == employee_id, Attendance.date == today).first()
    if existing and existing.check_in:
        raise ValueError("Already checked in today")
    status = AttendanceStatus.LATE.value if now.time() > _grace_cutoff(settings) \
        else AttendanceStatus.PRESENT.value
    if existing:
        existing.check_in = now
        existing.status = status
        existing.source = "web"
        db.commit(); db.refresh(existing); return existing
    a = Attendance(employee_id=employee_id, date=today, check_in=now,
                   status=status, source="web")
    db.add(a); db.commit(); db.refresh(a); return a


def check_out(db: Session, employee_id: int) -> Attendance:
    now = datetime.now()
    today = now.date()
    a = db.query(Attendance).filter(
        Attendance.employee_id == employee_id, Attendance.date == today).first()
    if not a or not a.check_in:
        raise ValueError("No check-in today")
    if a.check_out:
        raise ValueError("Already checked out today")
    a.check_out = now
    a.worked_minutes = int((now - a.check_in).total_seconds() / 60)
    settings = _settings(db)
    if a.worked_minutes < settings.half_day_hours * 60:
        a.status = AttendanceStatus.HALF_DAY.value
    db.commit(); db.refresh(a); return a


def today_record(db: Session, employee_id: int):
    return db.query(Attendance).filter(
        Attendance.employee_id == employee_id, Attendance.date == date.today()).first()


def calendar(db: Session, employee_id: int, year: int, month: int) -> list:
    settings = _settings(db)
    hol = holidays_set(db)
    start = date(year, month, 1)
    end = date(year, month, _calendar.monthrange(year, month)[1])
    recs = {r.date: r for r in db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= start, Attendance.date <= end).all()}
    leave_days = set()
    for lv in db.query(LeaveRequest).filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status == "approved",
            LeaveRequest.start_date <= end, LeaveRequest.end_date >= start).all():
        d = lv.start_date
        while d <= lv.end_date:
            leave_days.add(d); d += timedelta(days=1)
    out, cur, today = [], start, date.today()
    while cur <= end:
        rec = recs.get(cur)
        if rec and rec.check_in and rec.check_out:
            status = rec.status
        elif rec and rec.check_in and not rec.check_out:
            status = "missing_checkout" if cur < today else rec.status
        elif cur in leave_days:
            status = "on_leave"
        elif is_weekend(cur, settings.weekend):
            status = "weekend"
        elif cur in hol:
            status = "holiday"
        elif cur < today:
            status = "absent"
        else:
            status = None
        out.append({
            "date": cur.isoformat(), "status": status,
            "check_in": rec.check_in.isoformat() if rec and rec.check_in else None,
            "check_out": rec.check_out.isoformat() if rec and rec.check_out else None,
            "worked_minutes": rec.worked_minutes if rec else 0,
        })
        cur += timedelta(days=1)
    return out


def daily_board(db: Session, on_date: date) -> list:
    from app.models.user import User
    settings = _settings(db)
    hol = holidays_set(db)
    employees = (db.query(Employee).join(User)
                 .filter(User.is_active == True).all())
    recs = {r.employee_id: r for r in db.query(Attendance)
            .filter(Attendance.date == on_date).all()}
    leaves = {lv.employee_id: lv for lv in db.query(LeaveRequest).filter(
        LeaveRequest.status == "approved",
        LeaveRequest.start_date <= on_date,
        LeaveRequest.end_date >= on_date).all()}
    out = []
    for e in employees:
        rec = recs.get(e.id)
        lv = leaves.get(e.id)
        if rec and rec.check_in and rec.check_out:
            st = rec.status
        elif rec and rec.check_in:
            st = "missing_checkout" if on_date < date.today() else rec.status
        elif lv:
            st = "on_leave"
        elif is_weekend(on_date, settings.weekend):
            st = "weekend"
        elif on_date in hol:
            st = "holiday"
        elif on_date < date.today():
            st = "absent"
        else:
            st = None
        out.append({
            "employee_id": e.id, "employee_code": e.employee_code,
            "name": e.user.name, "department": e.department,
            "status": st,
            "check_in": rec.check_in.isoformat() if rec and rec.check_in else None,
            "check_out": rec.check_out.isoformat() if rec and rec.check_out else None,
            "worked_minutes": rec.worked_minutes if rec else 0,
        })
    return out


# ---------- Corrections ----------
def request_correction(db: Session, employee_id: int, data: dict) -> AttendanceCorrection:
    if data["date"] > date.today():
        raise ValueError("Correction date cannot be in the future")
    dup = db.query(AttendanceCorrection).filter(
        AttendanceCorrection.employee_id == employee_id,
        AttendanceCorrection.date == data["date"],
        AttendanceCorrection.status == "pending").first()
    if dup:
        raise ValueError("A pending correction already exists for this date")
    c = AttendanceCorrection(
        employee_id=employee_id, date=data["date"],
        requested_check_in=data.get("requested_check_in"),
        requested_check_out=data.get("requested_check_out"),
        reason=data["reason"])
    db.add(c); db.commit(); db.refresh(c); return c


def list_corrections(db: Session, employee_id: int = None, status: str = None):
    q = db.query(AttendanceCorrection)
    if employee_id: q = q.filter(AttendanceCorrection.employee_id == employee_id)
    if status: q = q.filter(AttendanceCorrection.status == status)
    return q.order_by(AttendanceCorrection.created_at.desc()).all()


def review_correction(db: Session, cid: int, reviewer_id: int,
                      action: str, comment: str | None) -> AttendanceCorrection:
    c = db.get(AttendanceCorrection, cid)
    if not c: raise LookupError("Correction not found")
    if c.status != "pending": raise ValueError("Already reviewed")
    c.status = "approved" if action == "approve" else "rejected"
    c.reviewed_by_id = reviewer_id
    c.review_comment = comment
    if action == "approve":
        settings = _settings(db)
        a = db.query(Attendance).filter(
            Attendance.employee_id == c.employee_id,
            Attendance.date == c.date).first()
        if not a:
            a = Attendance(employee_id=c.employee_id, date=c.date)
            db.add(a); db.flush()
        if c.requested_check_in: a.check_in = c.requested_check_in
        if c.requested_check_out: a.check_out = c.requested_check_out
        if a.check_in and a.check_out:
            a.worked_minutes = int((a.check_out - a.check_in).total_seconds() / 60)
        a.status = _compute_status(settings, a.check_in, a.check_out) if a.check_in else a.status
        a.source = "correction"
    db.commit(); db.refresh(c); return c