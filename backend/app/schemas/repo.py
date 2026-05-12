from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional
from .health_snapshot import HealthSnapshotOut

class RepoCreate(BaseModel):
    name: str
    local_path: str

class RepoOut(BaseModel):
    id: UUID
    name: str
    local_path: str
    last_analyzed: Optional[datetime] = None
    created_at: datetime
    latest_snapshot: Optional[HealthSnapshotOut] = None

    model_config = {"from_attributes": True}
