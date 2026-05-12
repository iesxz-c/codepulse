from sqlalchemy import String, DateTime, Integer, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    device_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    project: Mapped[str] = mapped_column(String, nullable=True)
    branch: Mapped[str] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    languages: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))

    device = relationship("Device", back_populates="sessions")
