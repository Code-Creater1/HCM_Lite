from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime
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
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)