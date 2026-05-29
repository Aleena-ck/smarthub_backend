from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class DocumentResponse(BaseModel):
    id: UUID
    workspace_id: UUID
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