from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Dict, Any

class HealthSnapshotOut(BaseModel):
    id: UUID
    repo_id: UUID
    taken_at: datetime
    test_coverage: float
    avg_complexity: float
    dead_code_count: int
    high_churn_files: List[Dict[str, Any]]
    health_score: float

    model_config = {"from_attributes": True}
