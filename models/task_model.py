from sqlalchemy import Column, String, DateTime, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid
import enum

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    due_date = Column(DateTime(timezone=True), nullable=True)
    reminder_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())