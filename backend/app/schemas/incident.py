from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class IncidentCreate(BaseModel):
    zone_id: UUID
    type: str
    priority: str = "medium"


class IncidentOut(BaseModel):
    id: UUID
    zone_id: UUID
    crew_id: Optional[UUID]
    type: str
    status: str
    priority: str
    reported_at: datetime

    class Config:
        from_attributes = True
