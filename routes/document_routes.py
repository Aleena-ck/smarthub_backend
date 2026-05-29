from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form,  Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from models.document_model import Document
from models.workspace_model import Workspace
from models.user_model import User
from schemas.document_schema import DocumentResponse, DocumentUploadResponse
from middleware.auth_middleware import get_current_user
from services.ai_service import AIService
from uuid import UUID
import os
import shutil
from datetime import datetime
from typing import Optional

router = APIRouter()
ai_service = AIService()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    workspace_id: str = Form(...),  # Changed to Form parameter
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find workspace by ID (could be UUID or numeric string)
    workspace = None
    
    # Try to find by UUID first
    try:
        workspace_uuid = UUID(workspace_id)
        workspace = db.query(Workspace).filter(
            Workspace.id == workspace_uuid,
            Workspace.user_id == current_user.id
        ).first()
    except ValueError:
        # Not a UUID, try to find by string ID (for local workspaces)
        # Get the first workspace for this user as fallback
        workspace = db.query(Workspace).filter(
            Workspace.user_id == current_user.id
        ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found. Please create a workspace first.")
    
    # Validate file size
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes")
    
    # Create unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record with user_id
    document = Document(
        workspace_id=workspace.id,  # Use the actual workspace UUID
        user_id=current_user.id,
        filename=file.filename,
        filepath=file_path,
        filetype=file.content_type or "application/octet-stream",
        size=size
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        filetype=document.filetype,
        size=document.size,
        message="File uploaded successfully"
    )

@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    workspace_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get documents for user"""
    query = db.query(Document).filter(Document.user_id == current_user.id)
    
    if workspace_id:
        query = query.filter(Document.workspace_id == workspace_id)
    
    documents = query.order_by(Document.created_at.desc()).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document metadata"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.get("/{document_id}/download")
def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document file"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.filepath):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=document.filepath,
        filename=document.filename,
        media_type=document.filetype
    )

@router.delete("/{document_id}")
def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from disk
    if os.path.exists(document.filepath):
        os.remove(document.filepath)
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}