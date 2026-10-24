from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.deps import require_roles, require_password_changed
from app.models.user import User, Role
from app.schemas.employee import EmployeeCreateIn, EmployeeUpdateSelfIn
from app.services import employee_service, audit_service

router = APIRouter(prefix="/employees", tags=["employees"])


# ---------- specific routes MUST come before /{emp_id} ----------
@router.get("/me")
def my_profile(db: Session = Depends(get_db),
               user: User = Depends(require_roles(Role.EMPLOYEE)),
               _: User = Depends(require_password_changed)):
    emp = employee_service.get_self(db, user.id)
    if not emp: raise HTTPException(404, "Employee profile not found")
    return employee_service.to_out(emp)


@router.patch("/me")
def update_me(payload: EmployeeUpdateSelfIn, db: Session = Depends(get_db),
              user: User = Depends(require_roles(Role.EMPLOYEE)),
              _: User = Depends(require_password_changed)):
    emp = employee_service.get_self(db, user.id)
    if not emp: raise HTTPException(404, "Employee profile not found")
    before = {"phone": emp.phone, "address": emp.address}
    emp = employee_service.update_self(db, emp, payload.phone, payload.address)
    audit_service.log(db, user.id, "UPDATE", "employee", emp.id,
                      before=before, after={"phone": emp.phone, "address": emp.address})
    return employee_service.to_out(emp)


@router.get("/export.csv")
def export(db: Session = Depends(get_db),
           _: User = Depends(require_roles(Role.HR))):
    csv = employee_service.export_csv(db)
    return Response(content=csv, media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=employees.csv"})


@router.post("/import/dry-run")
async def import_dry(file: UploadFile = File(...), db: Session = Depends(get_db),
                     _: User = Depends(require_roles(Role.HR))):
    b = await file.read()
    return employee_service.import_dry_run(db, b)


@router.post("/import/commit")
async def import_commit(file: UploadFile = File(...), db: Session = Depends(get_db),
                        hr: User = Depends(require_roles(Role.HR))):
    b = await file.read()
    result = employee_service.import_commit(db, b)
    if not result.get("committed"):
        raise HTTPException(422, detail=result)
    audit_service.log(db, hr.id, "IMPORT", "employee", None,
                      after={"created": result["created"]})
    return result


# ---------- generic ----------
@router.get("")
def list_all(search: str = None, page: int = 1, size: int = 20,
             db: Session = Depends(get_db),
             _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    return employee_service.list_employees(db, search, page, size)


@router.post("", status_code=201)
def create(payload: EmployeeCreateIn, db: Session = Depends(get_db),
           hr: User = Depends(require_roles(Role.HR))):
    try: emp = employee_service.register_employee(db, payload.model_dump())
    except ValueError as e: raise HTTPException(409, str(e))
    audit_service.log(db, hr.id, "CREATE", "employee", emp.id,
                      after={"code": emp.employee_code})
    return employee_service.to_out(emp)


@router.get("/{emp_id}")
def get_one(emp_id: int, db: Session = Depends(get_db),
            _: User = Depends(require_roles(Role.ADMIN, Role.HR))):
    p = employee_service.employee_360(db, emp_id)
    if not p: raise HTTPException(404, "Employee not found")
    return p