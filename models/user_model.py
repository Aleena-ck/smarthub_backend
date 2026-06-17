# models/user_model.py (UPDATED)

from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid
import enum

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    ADMIN = "ADMIN"

class PhoneOTPState(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    OTP_SENT = "OTP_SENT"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    phone_otp_state = Column(SQLEnum(PhoneOTPState), default=PhoneOTPState.UNVERIFIED)
    hashed_password = Column(String, nullable=True)  # NULL for Google-only accounts
    google_sub = Column(String(255), unique=True, nullable=True, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    avatar_meta = Column(JSON, nullable=True)  # See PDF schema
    settings = Column(JSON, default={
        "theme": "DARK",
        "ai_model": "llama3.2:8b",
        "notifications": {
            "email_calendar": True,
            "push_todo": True,
            "push_achievements": True
        },
        "ai_mode": "BALANCED"
    })
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())