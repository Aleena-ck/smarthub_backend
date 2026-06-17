# models/document_model.py (UPDATED)

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum as SQLEnum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid
import enum

class DocumentScope(str, enum.Enum):
    GLOBAL = "GLOBAL"
    SESSION = "SESSION"

class EmbeddingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    folder_id = Column(UUID(as_uuid=True), nullable=True)  # For GLOBAL scope
    session_id = Column(UUID(as_uuid=True), nullable=True)  # For SESSION scope
    scope = Column(SQLEnum(DocumentScope), nullable=False)
    original_filename = Column(String(512), nullable=False)
    storage_path = Column(String, nullable=False)
    mime_type = Column(String(128), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    chroma_collection = Column(String(255), nullable=True)
    embedding_status = Column(SQLEnum(EmbeddingStatus), default=EmbeddingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # CHECK constraint: GLOBAL scope requires folder_id, SESSION requires session_id
    __table_args__ = (
        CheckConstraint(
            "(scope = 'GLOBAL' AND folder_id IS NOT NULL AND session_id IS NULL) OR "
            "(scope = 'SESSION' AND session_id IS NOT NULL AND folder_id IS NULL)"
        ),
    )