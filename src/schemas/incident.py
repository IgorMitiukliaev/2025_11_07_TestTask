from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from core.enums import IncidentStatus, IncidentSource


class IncidentCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=4000)
    source: IncidentSource


class IncidentOut(BaseModel):
    id: UUID
    description: str
    status: IncidentStatus
    source: IncidentSource
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class IncidentStatusUpdate(BaseModel):
    status: IncidentStatus

class IncidentDescriptionUpdate(BaseModel):
    new_description: str = Field(..., min_length=1, max_length=500)