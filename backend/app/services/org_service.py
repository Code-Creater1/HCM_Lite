from sqlalchemy.orm import Session
from app.models.org import (CompanySettings, Department, Designation, LeaveType, Holiday)

# ---------- Settings ----------
def get_settings(db: Session) -> CompanySettings:
    s = db.query(CompanySettings).first()
    if not s:
        s = CompanySettings(company_name="HCM Lite Co.")
        db.add(s); db.commit(); db.refresh(s)
    return s

def update_settings(db: Session, **kw) -> CompanySettings:
    s = get_settings(db)
    for k, v in kw.items():
        if v is not None: setattr(s, k, v)
    db.commit(); db.refresh(s); return s

# ---------- Departments ----------
def create_department(db, name, code, description):
    if db.query(Department).filter((Department.name == name) | (Department.code == code)).first():
        raise ValueError("Department name or code already exists")
    d = Department(name=name, code=code, description=description)
    db.add(d); db.commit(); db.refresh(d); return d

def list_departments(db):
    return db.query(Department).order_by(Department.name).all()

def update_department(db, id, **kw):
    d = db.get(Department, id)
    if not d: raise LookupError("Department not found")
    for k, v in kw.items():
        if v is not None: setattr(d, k, v)
    db.commit(); db.refresh(d); return d

def delete_department(db, id):
    d = db.get(Department, id)
    if not d: raise LookupError("Department not found")
    db.delete(d); db.commit()

# ---------- Designations ----------
def create_designation(db, name, level):
    if db.query(Designation).filter(Designation.name == name).first():
        raise ValueError("Designation already exists")
    d = Designation(name=name, level=level)
    db.add(d); db.commit(); db.refresh(d); return d

def list_designations(db):
    return db.query(Designation).order_by(Designation.name).all()

def update_designation(db, id, **kw):
    d = db.get(Designation, id)
    if not d: raise LookupError("Designation not found")
    for k, v in kw.items():
        if v is not None: setattr(d, k, v)
    db.commit(); db.refresh(d); return d

def delete_designation(db, id):
    d = db.get(Designation, id)
    if not d: raise LookupError("Designation not found")
    db.delete(d); db.commit()

# ---------- Leave Types ----------
def create_leave_type(db, name, code, yearly_quota, is_paid):
    if db.query(LeaveType).filter((LeaveType.name == name) | (LeaveType.code == code)).first():
        raise ValueError("Leave type name or code already exists")
    d = LeaveType(name=name, code=code, yearly_quota=yearly_quota, is_paid=is_paid)
    db.add(d); db.commit(); db.refresh(d); return d

def list_leave_types(db):
    return db.query(LeaveType).order_by(LeaveType.name).all()

def update_leave_type(db, id, **kw):
    d = db.get(LeaveType, id)
    if not d: raise LookupError("Leave type not found")
    for k, v in kw.items():
        if v is not None: setattr(d, k, v)
    db.commit(); db.refresh(d); return d

def delete_leave_type(db, id):
    d = db.get(LeaveType, id)
    if not d: raise LookupError("Leave type not found")
    db.delete(d); db.commit()

# ---------- Holidays ----------
def create_holiday(db, name, date):
    if db.query(Holiday).filter(Holiday.date == date).first():
        raise ValueError("A holiday already exists on this date")
    h = Holiday(name=name, date=date)
    db.add(h); db.commit(); db.refresh(h); return h

def list_holidays(db):
    return db.query(Holiday).order_by(Holiday.date).all()

def delete_holiday(db, id):
    h = db.get(Holiday, id)
    if not h: raise LookupError("Holiday not found")
    db.delete(h); db.commit()