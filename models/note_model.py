from sqlalchemy import Column, String, DateTime, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # FIX: note_routes.py filters by Note.user_id on every GET/PUT/DELETE,
    # but this column never existed, causing a 500 AttributeError on every
    # single note fetch. Adding it directly (matching the Task model's
    # pattern) avoids needing a join through Workspace on every query.
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # FIX: previously only had onupdate=func.now(), meaning a freshly
    # created note had updated_at=NULL until its first edit. NoteResponse
    # requires updated_at as non-optional, so FastAPI/Pydantic rejected the
    # response on every create with a ResponseValidationError, even though
    # the row was already successfully inserted. server_default ensures it's
    # populated immediately, matching created_at on creation.
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())