# schemas/focus_schema.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

class FocusStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

class FocusSessionCreate(BaseModel):
    duration_seconds: int = Field(..., ge=60, le=14400)
    interval_seconds: Optional[int] = Field(None, ge=1)
    goal_description: Optional[str] = None

class FocusSessionComplete(BaseModel):
    milestone_payload: Optional[List[Dict[str, Any]]] = None

class FocusSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    duration_seconds: int
    interval_seconds: Optional[int]
    goal_description: Optional[str]
    status: FocusStatus
    actual_elapsed_seconds: Optional[int]
    milestone_payload: Optional[List[Dict[str, Any]]]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True