from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DeviceCreate(BaseModel):
    name: str

class DeviceOut(BaseModel):
    id: UUID
    name: str
    api_key_prefix: str
    created_at: datetime

    model_config = {"from_attributes": True}

class DeviceCreated(DeviceOut):
    api_key: str
