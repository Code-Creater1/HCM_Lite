import io
from datetime import date
import pandas as pd
from sqlalchemy.orm import Session

from app.models.user import User, Role
from app.models.employee import Employee
from app.models.org import Department
from app.core.security import hash_password


# ---------- core CRUD ----------
def register_employee(db: Session, data: dict) -> Employee:
    if db.query(User).filter(User.email == data["email"].lower()).first():
        raise ValueError("Email already in use")
    if db.query(Employee).filter(Employee.employee_code == data["employee_code"]).first():
        raise ValueError("Employee code already in use")
    u = User(email=data["email"].lower(), name=data["name"],
             password_hash=hash_password(data["temporary_password"]),
             role=Role.EMPLOYEE, is_active=True, must_change_password=True)
    db.add(u); db.flush()
    emp = Employee(user_id=u.id, employee_code=data["employee_code"],
                   department=data.get("department"), designation=data.get("designation"),
                   date_of_joining=data["date_of_joining"], basic_salary=data["basic_salary"],
                   phone=data.get("phone"), address=data.get("address"))
    db.add(emp); db.commit(); db.refresh(emp)
    return emp


def to_out(e: Employee) -> dict:
    return {"id": e.id, "user_id": e.user_id, "employee_code": e.employee_code,
            "name": e.user.name, "email": e.user.email, "department": e.department,
            "designation": e.designation, "date_of_joining": e.date_of_joining,
            "basic_salary": e.basic_salary, "phone": e.phone, "address": e.address}


def list_employees(db, search=None, page=1, size=20):
    q = db.query(Employee).join(User)
    if search:
        like = f"%{search}%"
        q = q.filter(User.name.ilike(like) | User.email.ilike(like) |
                     Employee.employee_code.ilike(like))
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return {"total": total, "page": page, "size": size,
            "items": [to_out(e) for e in items]}


def get_self(db, user_id):
    return db.query(Employee).filter(Employee.user_id == user_id).first()


def update_self(db, emp: Employee, phone, address):
    if phone is not None: emp.phone = phone
    if address is not None: emp.address = address
    db.commit(); db.refresh(emp); return emp


# ---------- 360 ----------
def get_by_id(db, emp_id):
    return db.query(Employee).filter(Employee.id == emp_id).first()


def employee_360(db, emp_id):
    e = get_by_id(db, emp_id)
    if not e: return None
    return {**to_out(e),
            "joined_days": (date.today() - e.date_of_joining).days,
            "status": "active" if e.user.is_active else "inactive"}


# ---------- CSV export ----------
def export_csv(db) -> str:
    rows = []
    for e in db.query(Employee).join(User).order_by(Employee.employee_code).all():
        rows.append({
            "employee_code": e.employee_code, "name": e.user.name, "email": e.user.email,
            "department": e.department or "", "designation": e.designation or "",
            "date_of_joining": e.date_of_joining.isoformat(),
            "basic_salary": e.basic_salary,
            "phone": e.phone or "", "address": e.address or "",
        })
    cols = ["employee_code", "name", "email", "department", "designation",
            "date_of_joining", "basic_salary", "phone", "address"]
    df = pd.DataFrame(rows, columns=cols)
    buf = io.StringIO(); df.to_csv(buf, index=False); return buf.getvalue()


# ---------- CSV import: dry run ----------
REQUIRED_COLS = ["name", "email", "employee_code", "department", "designation",
                 "date_of_joining", "basic_salary", "temporary_password"]


def import_dry_run(db, csv_bytes: bytes) -> dict:
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes), dtype=str, keep_default_na=False)
    except Exception as e:
        return {"rows_total": 0, "rows_ok": 0, "rows_error": 1,
                "errors": [{"row": 0, "field": "file",
                            "reason": f"Cannot parse CSV: {e}"}],
                "preview": []}

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        return {"rows_total": len(df), "rows_ok": 0, "rows_error": len(df) or 1,
                "errors": [{"row": 1, "field": "header",
                            "reason": f"Missing columns: {', '.join(missing)}"}],
                "preview": df.head(5).to_dict(orient="records")}

    errors, seen_codes, seen_emails = [], set(), set()
    db_codes = {c for (c,) in db.query(Employee.employee_code).all()}
    db_emails = {e for (e,) in db.query(User.email).all()}
    known_depts = {d for (d,) in db.query(Department.name).all()}

    for i, row in df.iterrows():
        row_num = i + 2
        for f in REQUIRED_COLS:
            if not str(row.get(f, "")).strip():
                errors.append({"row": row_num, "field": f, "reason": "required"})

        email = str(row.get("email", "")).strip().lower()
        if email:
            if "@" not in email or "." not in email.split("@")[-1]:
                errors.append({"row": row_num, "field": "email",
                               "reason": "invalid email format"})
            if email in seen_emails:
                errors.append({"row": row_num, "field": "email",
                               "reason": "duplicate within file"})
            if email in db_emails:
                errors.append({"row": row_num, "field": "email",
                               "reason": "already exists in DB"})
            seen_emails.add(email)

        code = str(row.get("employee_code", "")).strip()
        if code:
            if code in seen_codes:
                errors.append({"row": row_num, "field": "employee_code",
                               "reason": "duplicate within file"})
            if code in db_codes:
                errors.append({"row": row_num, "field": "employee_code",
                               "reason": "already exists in DB"})
            seen_codes.add(code)

        dj = str(row.get("date_of_joining", "")).strip()
        if dj:
            try: date.fromisoformat(dj)
            except Exception:
                errors.append({"row": row_num, "field": "date_of_joining",
                               "reason": "invalid ISO date (YYYY-MM-DD)"})

        sal = str(row.get("basic_salary", "")).strip()
        if sal:
            try:
                if float(sal) <= 0:
                    errors.append({"row": row_num, "field": "basic_salary",
                                   "reason": "must be > 0"})
            except Exception:
                errors.append({"row": row_num, "field": "basic_salary",
                               "reason": "not a number"})

        dept = str(row.get("department", "")).strip()
        if dept and known_depts and dept not in known_depts:
            errors.append({"row": row_num, "field": "department",
                           "reason": "unknown department (create it first)"})

        if len(str(row.get("temporary_password", "")).strip()) < 8:
            errors.append({"row": row_num, "field": "temporary_password",
                           "reason": "must be at least 8 characters"})

    bad_rows = {e["row"] for e in errors}
    rows_ok = max(0, len(df) - len(bad_rows))
    return {"rows_total": len(df), "rows_ok": rows_ok, "rows_error": len(bad_rows),
            "errors": errors, "preview": df.head(5).to_dict(orient="records")}


# ---------- CSV import: commit ----------
def import_commit(db, csv_bytes: bytes) -> dict:
    report = import_dry_run(db, csv_bytes)
    if report["rows_error"] > 0:
        return {"committed": False, **report}
    df = pd.read_csv(io.BytesIO(csv_bytes), dtype=str, keep_default_na=False)
    created = 0
    for _, row in df.iterrows():
        register_employee(db, {
            "name": str(row["name"]).strip(),
            "email": str(row["email"]).strip(),
            "employee_code": str(row["employee_code"]).strip(),
            "department": str(row["department"]).strip() or None,
            "designation": str(row["designation"]).strip() or None,
            "date_of_joining": date.fromisoformat(str(row["date_of_joining"]).strip()),
            "basic_salary": float(row["basic_salary"]),
            "phone": str(row.get("phone", "")).strip() or None,
            "address": str(row.get("address", "")).strip() or None,
            "temporary_password": str(row["temporary_password"]).strip(),
        })
        created += 1
    return {"committed": True, "created": created, **report}