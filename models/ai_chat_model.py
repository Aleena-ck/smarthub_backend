from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class AIChat(Base):
    __tablename__ = "ai_chats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=True)
    messages = Column(JSON, default=list)  # List of {role, content, timestamp}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())