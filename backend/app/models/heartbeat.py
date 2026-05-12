from sqlalchemy import String, DateTime, Boolean, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Heartbeat(Base):
    __tablename__ = "heartbeats"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    device_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    file: Mapped[str] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, nullable=True)
    project: Mapped[str] = mapped_column(String, nullable=True)
    branch: Mapped[str] = mapped_column(String, nullable=True)
    is_write: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))

    device = relationship("Device", back_populates="heartbeats")
