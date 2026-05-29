from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # ADD THIS
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())