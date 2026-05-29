from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class TaskCreate(BaseModel):
    workspace_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[datetime]
    reminder_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True