# services/achievement_service.py (NEW)

from sqlalchemy.orm import Session
from models.achievement_model import Achievement
from services.rabbitmq_service import publish_message
from uuid import UUID

ACHIEVEMENTS = {
    "FIRST_FOCUS": {"label": "First Focus", "condition": lambda sessions, seconds, streak: sessions >= 1},
    "WEEKLY_WARRIOR": {"label": "Weekly Warrior", "condition": lambda sessions, seconds, streak: sessions >= 5},
    "TEN_HOUR_CLUB": {"label": "10 Hour Club", "condition": lambda sessions, seconds, streak: seconds >= 36000},
    "MONTH_MASTER": {"label": "Month Master", "condition": lambda sessions, seconds, streak: streak >= 30},
}

async def check_and_award_achievements(
    db: Session,
    user_id: UUID,
    total_sessions: int,
    total_seconds: int,
    current_streak: int
):
    """Check and award new achievements"""
    
    newly_awarded = []
    
    for key, config in ACHIEVEMENTS.items():
        # Check if already awarded
        existing = db.query(Achievement).filter(
            Achievement.user_id == user_id,
            Achievement.achievement_key == key
        ).first()
        
        if not existing and config["condition"](total_sessions, total_seconds, current_streak):
            achievement = Achievement(
                user_id=user_id,
                achievement_key=key
            )
            db.add(achievement)
            newly_awarded.append({"key": key, "label": config["label"]})
    
    if newly_awarded:
        db.commit()
        
        # Send push notification
        await publish_message(
            exchange="cixio.topic",
            routing_key="push.achievements",
            payload={
                "event": "achievement.unlocked",
                "user_id": str(user_id),
                "achievements": newly_awarded
            }
        )
    
    return newly_awarded