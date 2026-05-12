from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID

class SummaryOut(BaseModel):
    id: UUID
    week_start: date
    content: str
    generated_at: datetime

    model_config = {"from_attributes": True}
