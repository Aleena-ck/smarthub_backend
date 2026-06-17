# schemas/document_schema.py

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class DocumentResponse(BaseModel):
    id: UUID
    workspace_id: Optional[UUID] = None  # Can be None for SESSION scope
    filename: str
    filetype: str
    size: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    filetype: str
    size: int
    message: str