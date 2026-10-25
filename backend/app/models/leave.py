from datetime import datetime, date
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    leave_type_id: Mapped[int] = mapped_column(ForeignKey("leave_types.id"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    days: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)