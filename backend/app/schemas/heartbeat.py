from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class HeartbeatIn(BaseModel):
    file: Optional[str] = None
    language: Optional[str] = None
    project: Optional[str] = None
    branch: Optional[str] = None
    is_write: bool = False
    time: datetime

class HeartbeatOut(HeartbeatIn):
    id: UUID
    device_id: UUID

    model_config = {"from_attributes": True}
