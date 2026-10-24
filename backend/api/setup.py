from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import FirstRunSetupIn, TokenOut, SetupStatusOut
from app.services import setup_service, auth_service, audit_service

router = APIRouter(prefix="/setup", tags=["setup"])

@router.get("/status", response_model=SetupStatusOut)
def status(db: Session = Depends(get_db)):
    return {"setup_completed": setup_service.setup_completed(db)}

@router.post("", response_model=TokenOut)
def first_run(payload: FirstRunSetupIn, db: Session = Depends(get_db)):
    try:
        admin = setup_service.first_run_setup(db, payload.company_name, payload.admin_name,
                                              payload.admin_email, payload.admin_password)
    except ValueError as e:
        raise HTTPException(409, str(e))
    audit_service.log(db, admin.id, "SETUP", "company",
                      after={"company_name": payload.company_name})
    return auth_service.token_response(admin)