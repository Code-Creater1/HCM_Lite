from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class DepartmentIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=20)
    description: Optional[str] = None

class DesignationIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    level: int = 1

class LeaveTypeIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    code: str = Field(min_length=1, max_length=20)
    yearly_quota: int = 0
    is_paid: bool = True

class HolidayIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date: date

class CompanySettingsUpdateIn(BaseModel):
    company_name: Optional[str] = None
    office_start: Optional[str] = None
    grace_minutes: Optional[int] = None
    half_day_hours: Optional[float] = None
    weekend: Optional[str] = None
    office_lat: Optional[float] = None
    office_lng: Optional[float] = None
    office_radius_m: Optional[int] = None