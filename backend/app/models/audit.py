from datetime import datetime
from sqlalchemy import String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    entity: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str] = mapped_column(String(50), nullable=True)
    before_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)