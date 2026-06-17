# routes/focus_routes.py (NEW)

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user_model import User
from models.focus_session_model import FocusSession, FocusStatus
from models.user_focus_stats_model import UserFocusStats
from models.achievement_model import Achievement
from schemas.focus_schema import FocusSessionCreate, FocusSessionComplete, FocusSessionResponse
from middleware.auth_middleware import get_current_user
from services.achievement_service import check_and_award_achievements
from services.rabbitmq_service import publish_message
from uuid import UUID
from datetime import datetime
import math

router = APIRouter()

@router.post("/sessions", response_model=FocusSessionResponse)
def start_focus_session(
    session_data: FocusSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new focus session"""
    
    # Validate duration
    if session_data.duration_seconds < 60 or session_data.duration_seconds > 14400:
        raise HTTPException(status_code=422, detail="duration_seconds must be between 60 and 14400")
    
    # Validate interval
    if session_data.interval_seconds and session_data.interval_seconds >= session_data.duration_seconds:
        raise HTTPException(status_code=422, detail="interval_seconds must be less than duration_seconds")
    
    session = FocusSession(
        user_id=current_user.id,
        duration_seconds=session_data.duration_seconds,
        interval_seconds=session_data.interval_seconds,
        goal_description=session_data.goal_description,
        status=FocusStatus.ACTIVE
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

@router.patch("/sessions/{session_id}/complete", response_model=dict)
async def complete_focus_session(
    session_id: UUID,
    completion_data: FocusSessionComplete,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a focus session and award achievements"""
    
    # Verify ownership
    session = db.query(FocusSession).filter(
        FocusSession.id == session_id,
        FocusSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found")
    
    if session.status != FocusStatus.ACTIVE:
        raise HTTPException(status_code=409, detail="Session already finalized")
    
    # Calculate actual elapsed time
    actual_elapsed = datetime.utcnow() - session.started_at
    actual_elapsed_seconds = min(int(actual_elapsed.total_seconds()), session.duration_seconds)
    
    # Update session
    session.status = FocusStatus.COMPLETED
    session.actual_elapsed_seconds = actual_elapsed_seconds
    session.completed_at = datetime.utcnow()
    
    if completion_data.milestone_payload:
        session.milestone_payload = completion_data.milestone_payload
    
    # Update user stats
    stats = db.query(UserFocusStats).filter(UserFocusStats.user_id == current_user.id).first()
    if not stats:
        stats = UserFocusStats(user_id=current_user.id)
        db.add(stats)
    
    stats.total_sessions += 1
    stats.total_seconds += actual_elapsed_seconds
    
    # Update streak
    today = datetime.utcnow().date()
    if stats.last_session_date:
        last_date = stats.last_session_date.date()
        if (today - last_date).days == 1:
            stats.current_streak_days += 1
        elif (today - last_date).days > 1:
            stats.current_streak_days = 1
    else:
        stats.current_streak_days = 1
    
    if stats.current_streak_days > stats.longest_streak_days:
        stats.longest_streak_days = stats.current_streak_days
    
    stats.last_session_date = datetime.utcnow()
    
    db.commit()
    
    # Check and award achievements (in background)
    background_tasks.add_task(
        check_and_award_achievements,
        db,
        current_user.id,
        stats.total_sessions,
        stats.total_seconds,
        stats.current_streak_days
    )
    
    # Invalidate dashboard cache
    background_tasks.add_task(invalidate_dashboard_cache, current_user.id)
    
    return {
        "session_id": str(session.id),
        "actual_elapsed_seconds": actual_elapsed_seconds,
        "total_sessions": stats.total_sessions,
        "total_minutes": stats.total_seconds // 60
    }