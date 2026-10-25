from datetime import datetime, date as date_type
from sqlalchemy import String, Integer, Float, DateTime, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CompanySettings(Base):
    __tablename__ = "company_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255))
    office_start: Mapped[str] = mapped_column(String(5), default="09:00")
    grace_minutes: Mapped[int] = mapped_column(Integer, default=15)
    half_day_hours: Mapped[float] = mapped_column(Float, default=5.0)
    weekend: Mapped[str] = mapped_column(String(50), default="Sat,Sun")
    office_lat: Mapped[float] = mapped_column(Float, nullable=True)
    office_lng: Mapped[float] = mapped_column(Float, nullable=True)
    office_radius_m: Mapped[int] = mapped_column(Integer, default=150)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Designation(Base):
    __tablename__ = "designations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    level: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LeaveType(Base):
    __tablename__ = "leave_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    yearly_quota: Mapped[int] = mapped_column(Integer, default=0)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Holiday(Base):
    __tablename__ = "holidays"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    date: Mapped[date_type] = mapped_column(Date, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)