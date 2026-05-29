# backend/schemas/workspace_schema.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class WorkspaceType(str, Enum):
    GENERAL = "general"
    PROJECT = "project"

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    icon: Optional[str] = "📁"
    color: Optional[str] = "#0080FF"

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[WorkspaceType] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    type: WorkspaceType
    icon: str
    color: str
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None  # Make optional

    class Config:
        from_attributes = True