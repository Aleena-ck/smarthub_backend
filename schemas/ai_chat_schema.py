from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class ChatRequest(BaseModel):
    prompt: str
    workspace_id: Optional[UUID] = None
    chat_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    response: str
    chat_id: UUID

class AIChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class AIChatCreate(BaseModel):
    workspace_id: Optional[UUID] = None
    title: Optional[str] = None

class AIChatResponse(BaseModel):
    id: UUID
    workspace_id: Optional[UUID]
    user_id: UUID
    title: Optional[str]
    messages: List[AIChatMessage]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True