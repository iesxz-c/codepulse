from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict

class SessionOut(BaseModel):
    id: UUID
    device_id: UUID
    project: Optional[str] = None
    branch: Optional[str] = None
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    languages: Dict[str, int]

    model_config = {"from_attributes": True}
