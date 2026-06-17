# models/focus_session_model.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid
import enum

class FocusStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"

class FocusSession(Base):
    __tablename__ = "focus_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    duration_seconds = Column(Integer, nullable=False)  # min 60, max 14400
    interval_seconds = Column(Integer, nullable=True)  # Pomodoro interval
    goal_description = Column(String, nullable=True)
    status = Column(SQLEnum(FocusStatus), default=FocusStatus.ACTIVE)
    actual_elapsed_seconds = Column(Integer, nullable=True)
    milestone_payload = Column(JSON, default=list)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)