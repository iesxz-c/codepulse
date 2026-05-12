from sqlalchemy import Float, Integer, DateTime, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import datetime

class HealthSnapshot(Base):
    __tablename__ = "health_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    repo_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    test_coverage: Mapped[float] = mapped_column(Float, server_default=text("0"))
    avg_complexity: Mapped[float] = mapped_column(Float, server_default=text("0"))
    dead_code_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    high_churn_files: Mapped[list] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    health_score: Mapped[float] = mapped_column(Float, server_default=text("0"))

    repo = relationship("Repo", back_populates="snapshots")
