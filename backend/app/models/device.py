from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    api_key_prefix: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    
    heartbeats = relationship("Heartbeat", back_populates="device", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="device", cascade="all, delete-orphan")
