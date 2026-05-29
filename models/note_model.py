from sqlalchemy import Column, String, DateTime, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())