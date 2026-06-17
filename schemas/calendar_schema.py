# schemas/calendar_schema.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum

class NotificationMode(str, Enum):
    TIME_BASED = "TIME_BASED"
    DAY_START = "DAY_START"

class RecurrenceFrequency(str, Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class RecurrenceRule(BaseModel):
    freq: RecurrenceFrequency
    interval: int = 1
    byday: Optional[List[str]] = None
    until: Optional[datetime] = None

class CalendarEventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    is_all_day: bool = False
    recurrence_rule: Optional[RecurrenceRule] = None
    linked_todo_id: Optional[UUID] = None
    notification_mode: NotificationMode = NotificationMode.TIME_BASED

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_all_day: Optional[bool] = None
    recurrence_rule: Optional[RecurrenceRule] = None
    linked_todo_id: Optional[UUID] = None
    notification_mode: Optional[NotificationMode] = None

class CalendarEventResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    is_all_day: bool
    recurrence_rule: Optional[dict]
    linked_todo_id: Optional[UUID]
    notification_mode: NotificationMode
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True