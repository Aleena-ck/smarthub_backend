from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class TaskPriority(str, Enum):
    LOW = "LOW"              # ✅ Changed from "low" to "LOW"
    MEDIUM = "MEDIUM"        # ✅ Changed from "medium" to "MEDIUM"
    HIGH = "HIGH"            # ✅ Changed from "high" to "HIGH"
    CRITICAL = "CRITICAL"    # ✅ Already correct

class TaskStatus(str, Enum):
    PENDING = "PENDING"              # ✅ Changed from "pending" to "PENDING"
    IN_PROGRESS = "IN_PROGRESS"      # ✅ Changed from "in_progress" to "IN_PROGRESS"
    COMPLETED = "COMPLETED"          # ✅ Changed from "completed" to "COMPLETED"
    CANCELLED = "CANCELLED"          # ✅ Changed from "archived" to "CANCELLED" (match frontend)

class TaskCreate(BaseModel):
    workspace_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    deadline: Optional[datetime] = None  # ← Changed from due_date
    reminder_at: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    deadline: Optional[datetime] = None 
    reminder_at: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    description: Optional[str]
    priority: TaskPriority
    status: TaskStatus
    deadline: Optional[datetime] = None  # ← Changed from due_date
    reminder_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True