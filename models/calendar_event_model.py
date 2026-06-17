from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid
import enum

class NotificationMode(str, enum.Enum):
    TIME_BASED = "TIME_BASED"
    DAY_START = "DAY_START"

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    is_all_day = Column(Boolean, default=False)
    recurrence_rule = Column(JSON, nullable=True)  # RFC 5545 RRULE
    linked_todo_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    notification_mode = Column(SQLEnum(NotificationMode), default=NotificationMode.TIME_BASED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())