import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Role(str, enum.Enum):
    ADMIN = "ADMIN"; HR = "HR"; EMPLOYEE = "EMPLOYEE"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", back_populates="user", uselist=False)