from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from models.device_token_model import DeviceToken
from models.user_model import User
from middleware.auth_middleware import get_current_user
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

class TokenRegister(BaseModel):
    token: str
    device_type: str = "android"

@router.post("/register-token")
def register_device_token(
    token_data: TokenRegister,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register device token for push notifications"""
    # Check if token already exists
    existing = db.query(DeviceToken).filter(DeviceToken.token == token_data.token).first()
    if existing:
        # Update existing token
        existing.user_id = current_user.id
        existing.device_type = token_data.device_type
        db.commit()
        return {"message": "Token updated"}
    
    # Create new token
    device_token = DeviceToken(
        token=token_data.token,
        user_id=current_user.id,
        device_type=token_data.device_type
    )
    db.add(device_token)
    db.commit()
    return {"message": "Token registered successfully"}

@router.delete("/tokens")
def delete_device_token(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete device token"""
    device_token = db.query(DeviceToken).filter(
        DeviceToken.token == token,
        DeviceToken.user_id == current_user.id
    ).first()
    
    if device_token:
        db.delete(device_token)
        db.commit()
    
    return {"message": "Token deleted successfully"}

@router.get("/tokens")
def get_device_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all device tokens for current user"""
    tokens = db.query(DeviceToken).filter(DeviceToken.user_id == current_user.id).all()
    return {"tokens": [{"id": t.id, "device_type": t.device_type} for t in tokens]}