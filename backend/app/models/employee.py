from datetime import datetime, date
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    employee_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    department: Mapped[str] = mapped_column(String(100), nullable=True)
    designation: Mapped[str] = mapped_column(String(100), nullable=True)
    date_of_joining: Mapped[date] = mapped_column(Date)
    basic_salary: Mapped[float] = mapped_column(Float, default=0)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="employee")