from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class EmployeeCreateIn(BaseModel):
    name: str
    email: EmailStr
    employee_code: str
    department: str
    designation: str
    date_of_joining: date
    basic_salary: float = Field(gt=0)
    phone: Optional[str] = None
    address: Optional[str] = None
    temporary_password: str = Field(min_length=8)

class EmployeeUpdateSelfIn(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None

class HRLoginCreateIn(BaseModel):
    name: str
    email: EmailStr
    temporary_password: str = Field(min_length=8)