from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.org import CompanySettings, Holiday

_WEEKDAY_MAP = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


def is_weekend(d: date, weekend_str: str) -> bool:
    return d.weekday() in [_WEEKDAY_MAP[n.strip()] for n in weekend_str.split(",")
                           if n.strip() in _WEEKDAY_MAP]


def holidays_set(db: Session) -> set:
    return {h.date for h in db.query(Holiday).all()}


def working_days_list(db: Session, start: date, end: date) -> list:
    s = db.query(CompanySettings).first()
    weekend_str = s.weekend if s else "Sat,Sun"
    hol = holidays_set(db)
    out = []
    cur = start
    while cur <= end:
        if not is_weekend(cur, weekend_str) and cur not in hol:
            out.append(cur)
        cur += timedelta(days=1)
    return out


def count_working_days(db: Session, start: date, end: date) -> int:
    return len(working_days_list(db, start, end))