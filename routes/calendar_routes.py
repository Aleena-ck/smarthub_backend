# routes/calendar_routes.py (NEW)

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user_model import User
from models.calendar_event_model import CalendarEvent, NotificationMode
from models.task_model import Task
from schemas.calendar_schema import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
from middleware.auth_middleware import get_current_user
from services.rabbitmq_service import publish_delayed_message
from uuid import UUID
from datetime import datetime, timedelta
import json

router = APIRouter()

@router.post("/events", response_model=CalendarEventResponse)
async def create_calendar_event(
    event: CalendarEventCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a calendar event with notification scheduling"""
    
    # Validate end_time > start_time
    if event.end_time and event.end_time <= event.start_time:
        raise HTTPException(status_code=422, detail="end_time must be greater than start_time")
    
    # Validate linked_todo belongs to user
    if event.linked_todo_id:
        todo = db.query(Task).filter(
            Task.id == event.linked_todo_id,
            Task.user_id == current_user.id
        ).first()
        if not todo:
            raise HTTPException(status_code=422, detail="linked_todo_id not found")
    
    # Normalize all-day events
    start_time = event.start_time
    if event.is_all_day:
        start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create event
    db_event = CalendarEvent(
        user_id=current_user.id,
        title=event.title,
        description=event.description,
        start_time=start_time,
        end_time=event.end_time,
        is_all_day=event.is_all_day,
        recurrence_rule=event.recurrence_rule.dict() if event.recurrence_rule else None,
        linked_todo_id=event.linked_todo_id,
        notification_mode=event.notification_mode
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Schedule notifications based on mode
    if event.notification_mode == NotificationMode.TIME_BASED:
        # Send notification 1 hour before
        notify_at = start_time - timedelta(hours=1)
        if notify_at > datetime.utcnow():
            background_tasks.add_task(
                publish_delayed_message,
                exchange="cixio.delayed",
                routing_key="cal.notify",
                payload={
                    "event": "cal.notify",
                    "user_id": str(current_user.id),
                    "event_id": str(db_event.id),
                    "title": event.title,
                    "start_time": start_time.isoformat(),
                    "type": "email"
                },
                delay_ms=int((notify_at - datetime.utcnow()).total_seconds() * 1000)
            )
    
    elif event.notification_mode == NotificationMode.DAY_START:
        # Add to daily digest queue
        background_tasks.add_task(
            publish_delayed_message,
            exchange="cixio.topic",
            routing_key="cal.digest",
            payload={
                "event": "cal.digest",
                "user_id": str(current_user.id),
                "event_id": str(db_event.id),
                "title": event.title,
                "event_date": start_time.date().isoformat()
            },
            delay_ms=0
        )
    
    # Invalidate dashboard cache
    background_tasks.add_task(invalidate_dashboard_cache, current_user.id)
    
    return db_event

@router.get("/events")
def get_calendar_events(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar events within date range"""
    events = db.query(CalendarEvent).filter(
        CalendarEvent.user_id == current_user.id,
        CalendarEvent.start_time >= start_date,
        CalendarEvent.start_time <= end_date
    ).order_by(CalendarEvent.start_time).all()
    
    return events