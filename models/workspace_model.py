from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base
import uuid
import enum

class WorkspaceType(str, enum.Enum):
    GENERAL = "general"
    PROJECT = "project"

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(Enum(WorkspaceType), default=WorkspaceType.GENERAL)
    icon = Column(String, default="📁")
    color = Column(String, default="#0080FF")
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 