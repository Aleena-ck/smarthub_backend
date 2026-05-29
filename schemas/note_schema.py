from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class NoteCreate(BaseModel):
    workspace_id: UUID
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = False

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

class NoteResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    title: str
    content: Optional[str]
    tags: Optional[List[str]]
    is_favorite: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True