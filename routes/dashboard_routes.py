# routes/dashboard_routes.py (NEW)

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.connection import get_db
from models.user_model import User
from middleware.auth_middleware import get_current_user
from services.redis_service import get_cache, set_cache
from uuid import UUID
from datetime import datetime, timedelta
import json

router = APIRouter()

def get_iso_week(date: datetime) -> str:
    """Get ISO week number for cache key"""
    return f"{date.year}-W{date.isocalendar()[1]:02d}"

@router.get("/")
async def get_dashboard(
    week_offset: int = Query(0, ge=0, le=52),
    include_feeds: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard with aggregated data"""
    
    target_date = datetime.utcnow() + timedelta(weeks=week_offset)
    cache_key = f"dashboard:{current_user.id}:{get_iso_week(target_date)}"
    
    # Check cache
    cached = await get_cache(cache_key)
    if cached:
        return {"data": json.loads(cached), "cache": "HIT"}
    
    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Query A: Today's items
    today_items = db.execute(
        text("""
            SELECT id, title, deadline, status, priority, 'todo' as type
            FROM todos 
            WHERE user_id = :user_id 
                AND DATE(deadline AT TIME ZONE 'UTC') = CURRENT_DATE 
                AND status NOT IN ('COMPLETED', 'CANCELLED')
            UNION ALL
            SELECT id, title, start_time, NULL, NULL, 'event' as type
            FROM calendar_events 
            WHERE user_id = :user_id 
                AND DATE(start_time AT TIME ZONE 'UTC') = CURRENT_DATE
            ORDER BY coalesce(deadline, start_time) ASC
        """),
        {"user_id": current_user.id}
    ).fetchall()
    
    # Query B: Recent activity (last 7 days)
    recent_activity = db.execute(
        text("""
            SELECT entity_type, id, title, updated_at FROM (
                SELECT 'todo' as entity_type, id, title, updated_at 
                FROM todos WHERE user_id = :user_id AND updated_at >= :week_ago
                UNION ALL
                SELECT 'note' as entity_type, id, title, updated_at 
                FROM notes WHERE user_id = :user_id AND updated_at >= :week_ago
                UNION ALL
                SELECT 'focus' as entity_type, id, goal_description as title, completed_at as updated_at 
                FROM focus_sessions 
                WHERE user_id = :user_id AND completed_at >= :week_ago AND status = 'COMPLETED'
            ) combined 
            ORDER BY updated_at DESC LIMIT 20
        """),
        {"user_id": current_user.id, "week_ago": week_ago}
    ).fetchall()
    
    # Query C: Future activities (next 30 days)
    future_activities = db.execute(
        text("""
            SELECT 'todo' as type, id, title, deadline as event_time
            FROM todos 
            WHERE user_id = :user_id 
                AND deadline BETWEEN now() AND now() + interval '30 days'
                AND status NOT IN ('COMPLETED', 'CANCELLED')
            UNION ALL
            SELECT 'event' as type, id, title, start_time as event_time
            FROM calendar_events 
            WHERE user_id = :user_id 
                AND start_time BETWEEN now() AND now() + interval '30 days'
            ORDER BY event_time ASC
        """),
        {"user_id": current_user.id}
    ).fetchall()
    
    # Query D: User achievements
    achievements = db.execute(
        text("""
            SELECT achievement_key, awarded_at
            FROM achievements 
            WHERE user_id = :user_id
            ORDER BY awarded_at DESC LIMIT 10
        """),
        {"user_id": current_user.id}
    ).fetchall()
    
    # Calculate aggregated counters
    weekly_focus = db.execute(
        text("""
            SELECT COALESCE(SUM(actual_elapsed_seconds) / 60, 0) as minutes
            FROM focus_sessions 
            WHERE user_id = :user_id 
                AND status = 'COMPLETED'
                AND DATE_TRUNC('week', completed_at) = DATE_TRUNC('week', CURRENT_DATE)
        """),
        {"user_id": current_user.id}
    ).scalar()
    
    monthly_completion = db.execute(
        text("""
            SELECT 
                COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END)::float / 
                NULLIF(COUNT(*), 0)::float as rate
            FROM todos 
            WHERE user_id = :user_id 
                AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
        """),
        {"user_id": current_user.id}
    ).scalar()
    
    weekly_notes = db.execute(
        text("""
            SELECT COUNT(*) as count
            FROM notes 
            WHERE user_id = :user_id 
                AND DATE_TRUNC('week', created_at) = DATE_TRUNC('week', CURRENT_DATE)
        """),
        {"user_id": current_user.id}
    ).scalar()
    
    payload = {
        "today_items": [dict(row._mapping) for row in today_items],
        "recent_activity": [dict(row._mapping) for row in recent_activity],
        "future_activities": [dict(row._mapping) for row in future_activities],
        "achievements": [dict(row._mapping) for row in achievements],
        "counters": {
            "weekly_focus_minutes": weekly_focus or 0,
            "monthly_todo_completion_rate": monthly_completion or 0,
            "weekly_notes_created": weekly_notes or 0
        }
    }
    
    # Cache for 5 minutes (300 seconds)
    await set_cache(cache_key, json.dumps(payload), ttl=300)
    
    return {"data": payload, "cache": "MISS"}