import enum
from datetime import datetime, date as date_type
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    LATE = "late"
    HALF_DAY = "half_day"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("employee_id", "date", name="uq_attendance_emp_date"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    date: Mapped[date_type] = mapped_column(Date, index=True)
    check_in: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    check_out: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="present")
    source: Mapped[str] = mapped_column(String(20), default="web")
    worked_minutes: Mapped[int] = mapped_column(Integer, default=0)


class AttendanceCorrection(Base):
    __tablename__ = "attendance_corrections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), index=True)
    date: Mapped[date_type] = mapped_column(Date)
    requested_check_in: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    requested_check_out: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    reviewed_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)