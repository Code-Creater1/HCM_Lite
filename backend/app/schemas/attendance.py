from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class CorrectionIn(BaseModel):
    date: date
    requested_check_in: Optional[datetime] = None
    requested_check_out: Optional[datetime] = None
    reason: str = Field(min_length=3, max_length=1000)


class CorrectionReviewIn(BaseModel):
    action: str  # "approve" | "reject"
    comment: Optional[str] = None