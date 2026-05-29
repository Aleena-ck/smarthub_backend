from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user_model import User
from models.ai_chat_model import AIChat
from schemas.ai_chat_schema import ChatRequest, ChatResponse, AIChatCreate, AIChatResponse, AIChatMessage
from middleware.auth_middleware import get_current_user
from services.ai_service import AIService
from uuid import UUID
from typing import Optional

router = APIRouter()
ai_service = AIService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message to AI"""
    response, chat_id = await ai_service.chat(
        db=db,
        user_id=current_user.id,
        prompt=request.prompt,
        workspace_id=request.workspace_id,
        chat_id=request.chat_id
    )
    
    return ChatResponse(response=response, chat_id=chat_id)

@router.post("/analyze-document")
async def analyze_document(
    document_id: UUID,
    prompt: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze a document with AI"""
    from models.document_model import Document
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Extract text from document (simplified - would need proper parsing)
    # For now, return a placeholder response
    analysis = await ai_service.ollama.analyze_document(
        content=f"[Document: {document.filename}]",
        prompt=prompt
    )
    
    return {"analysis": analysis}

@router.get("/chats", response_model=list[AIChatResponse])
def get_chats(
    workspace_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's AI chat sessions"""
    query = db.query(AIChat).filter(AIChat.user_id == current_user.id)
    
    if workspace_id:
        query = query.filter(AIChat.workspace_id == workspace_id)
    
    chats = query.order_by(AIChat.updated_at.desc()).all()
    
    # Convert messages to proper format
    for chat in chats:
        if chat.messages:
            chat.messages = [
                AIChatMessage(**msg) if isinstance(msg, dict) else msg
                for msg in chat.messages
            ]
    
    return chats

@router.post("/chats", response_model=AIChatResponse)
def create_chat(
    chat_data: AIChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new AI chat session"""
    chat = AIChat(
        user_id=current_user.id,
        workspace_id=chat_data.workspace_id,
        title=chat_data.title or "New Chat",
        messages=[]
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    
    return chat

@router.get("/chats/{chat_id}", response_model=AIChatResponse)
def get_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat session with history"""
    chat = db.query(AIChat).filter(
        AIChat.id == chat_id,
        AIChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    if chat.messages:
        chat.messages = [
            AIChatMessage(**msg) if isinstance(msg, dict) else msg
            for msg in chat.messages
        ]
    
    return chat

@router.delete("/chats/{chat_id}")
def delete_chat(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    chat = db.query(AIChat).filter(
        AIChat.id == chat_id,
        AIChat.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"message": "Chat deleted successfully"}

@router.get("/daily-insight")
async def get_daily_insight(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI daily productivity insight"""
    insight = await ai_service.get_daily_insight(db, current_user.id)
    return {"insight": insight}

@router.get("/weekly-report")
async def get_weekly_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI weekly productivity report"""
    report = await ai_service.get_weekly_report(db, current_user.id)
    return {"report": report}