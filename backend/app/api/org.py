from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require_roles
from app.models.user import User, Role
from app.schemas.org import (DepartmentIn, DesignationIn, LeaveTypeIn,
                             HolidayIn, CompanySettingsUpdateIn)
from app.services import org_service, audit_service

router = APIRouter(prefix="/org", tags=["org"])

def _admin(u: User = Depends(require_roles(Role.ADMIN))) -> User: return u

# ---------- Settings ----------
@router.get("/settings")
def get_settings(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    s = org_service.get_settings(db)
    return {"company_name": s.company_name, "office_start": s.office_start,
            "grace_minutes": s.grace_minutes, "half_day_hours": s.half_day_hours,
            "weekend": s.weekend, "office_lat": s.office_lat,
            "office_lng": s.office_lng, "office_radius_m": s.office_radius_m}

@router.patch("/settings")
def update_settings(payload: CompanySettingsUpdateIn, db: Session = Depends(get_db),
                    admin: User = Depends(_admin)):
    s = org_service.update_settings(db, **payload.model_dump())
    audit_service.log(db, admin.id, "UPDATE", "company_settings", s.id,
                     after=payload.model_dump(exclude_none=True))
    return {"status": "ok"}

# ---------- Departments ----------
@router.get("/departments")
def list_depts(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    return [{"id": d.id, "name": d.name, "code": d.code, "description": d.description}
            for d in org_service.list_departments(db)]

@router.post("/departments", status_code=201)
def create_dept(p: DepartmentIn, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: d = org_service.create_department(db, p.name, p.code, p.description)
    except ValueError as e: raise HTTPException(409, str(e))
    audit_service.log(db, admin.id, "CREATE", "department", d.id, after={"name": d.name})
    return {"id": d.id, "name": d.name, "code": d.code, "description": d.description}

@router.patch("/departments/{id}")
def update_dept(id: int, p: DepartmentIn, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: d = org_service.update_department(db, id, **p.model_dump())
    except LookupError as e: raise HTTPException(404, str(e))
    audit_service.log(db, admin.id, "UPDATE", "department", id, after=p.model_dump())
    return {"id": d.id, "name": d.name, "code": d.code, "description": d.description}

@router.delete("/departments/{id}", status_code=204)
def delete_dept(id: int, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: org_service.delete_department(db, id)
    except LookupError as e: raise HTTPException(404, str(e))
    audit_service.log(db, admin.id, "DELETE", "department", id)

# ---------- Designations ----------
@router.get("/designations")
def list_desigs(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    return [{"id": d.id, "name": d.name, "level": d.level} for d in org_service.list_designations(db)]

@router.post("/designations", status_code=201)
def create_desig(p: DesignationIn, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: d = org_service.create_designation(db, p.name, p.level)
    except ValueError as e: raise HTTPException(409, str(e))
    audit_service.log(db, admin.id, "CREATE", "designation", d.id, after={"name": d.name})
    return {"id": d.id, "name": d.name, "level": d.level}

@router.delete("/designations/{id}", status_code=204)
def delete_desig(id: int, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: org_service.delete_designation(db, id)
    except LookupError as e: raise HTTPException(404, str(e))
    audit_service.log(db, admin.id, "DELETE", "designation", id)

# ---------- Leave Types ----------
@router.get("/leave-types")
def list_lt(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    return [{"id": d.id, "name": d.name, "code": d.code,
             "yearly_quota": d.yearly_quota, "is_paid": d.is_paid}
            for d in org_service.list_leave_types(db)]

@router.post("/leave-types", status_code=201)
def create_lt(p: LeaveTypeIn, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: d = org_service.create_leave_type(db, p.name, p.code, p.yearly_quota, p.is_paid)
    except ValueError as e: raise HTTPException(409, str(e))
    audit_service.log(db, admin.id, "CREATE", "leave_type", d.id, after={"name": d.name})
    return {"id": d.id, "name": d.name, "code": d.code,
            "yearly_quota": d.yearly_quota, "is_paid": d.is_paid}

@router.delete("/leave-types/{id}", status_code=204)
def delete_lt(id: int, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: org_service.delete_leave_type(db, id)
    except LookupError as e: raise HTTPException(404, str(e))
    audit_service.log(db, admin.id, "DELETE", "leave_type", id)

# ---------- Holidays ----------
@router.get("/holidays")
def list_hol(db: Session = Depends(get_db), _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    return [{"id": h.id, "name": h.name, "date": h.date.isoformat()}
            for h in org_service.list_holidays(db)]

@router.post("/holidays", status_code=201)
def create_hol(p: HolidayIn, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: h = org_service.create_holiday(db, p.name, p.date)
    except ValueError as e: raise HTTPException(409, str(e))
    audit_service.log(db, admin.id, "CREATE", "holiday", h.id, after={"name": h.name})
    return {"id": h.id, "name": h.name, "date": h.date.isoformat()}

@router.delete("/holidays/{id}", status_code=204)
def delete_hol(id: int, db: Session = Depends(get_db), admin: User = Depends(_admin)):
    try: org_service.delete_holiday(db, id)
    except LookupError as e: raise HTTPException(404, str(e))
    audit_service.log(db, admin.id, "DELETE", "holiday", id)