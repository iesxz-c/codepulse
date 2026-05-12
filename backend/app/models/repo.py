from sqlalchemy import String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class Repo(Base):
    __tablename__ = "repos"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    local_path: Mapped[str] = mapped_column(String, nullable=False)
    last_analyzed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    snapshots = relationship("HealthSnapshot", back_populates="repo", cascade="all, delete-orphan")
