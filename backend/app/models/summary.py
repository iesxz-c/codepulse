from sqlalchemy import String, DateTime, Date, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import date, datetime

class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    week_start: Mapped[date] = mapped_column(Date, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
