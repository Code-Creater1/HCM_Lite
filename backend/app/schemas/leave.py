from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class LeaveApplyIn(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=1000)


class LeaveReviewIn(BaseModel):
    action: str  # "approve" | "reject"
    comment: Optional[str] = None