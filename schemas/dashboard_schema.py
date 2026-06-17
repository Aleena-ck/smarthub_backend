# schemas/dashboard_schema.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

class TodayItem(BaseModel):
    id: UUID
    title: str
    deadline: Optional[datetime]
    status: Optional[str]
    priority: Optional[str]
    type: str  # "todo" or "event"

class RecentActivityItem(BaseModel):
    entity_type: str
    id: UUID
    title: str
    updated_at: datetime

class FutureActivityItem(BaseModel):
    type: str
    id: UUID
    title: str
    event_time: datetime

class AchievementItem(BaseModel):
    achievement_key: str
    awarded_at: datetime

class DashboardCounters(BaseModel):
    weekly_focus_minutes: int
    monthly_todo_completion_rate: float
    weekly_notes_created: int

class DashboardResponse(BaseModel):
    today_items: List[TodayItem]
    recent_activity: List[RecentActivityItem]
    future_activities: List[FutureActivityItem]
    achievements: List[AchievementItem]
    counters: DashboardCounters