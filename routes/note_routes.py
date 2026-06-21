from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.note_model import Note
from models.workspace_model import Workspace
from models.user_model import User
from schemas.note_schema import NoteCreate, NoteUpdate, NoteResponse
from middleware.auth_middleware import get_current_user
from uuid import UUID
from typing import Optional

router = APIRouter()

@router.post("/", response_model=NoteResponse)
def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new note"""
    workspace = db.query(Workspace).filter(
        Workspace.id == note.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # FIX: user_id must be set explicitly — NoteCreate schema (and therefore
    # note.model_dump()) has no user_id field, so it must come from the
    # authenticated user, not from client input.
    db_note = Note(**note.model_dump(), user_id=current_user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/")
def get_notes(
    workspace_id: Optional[UUID] = Query(None),
    favorite: Optional[bool] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notes with optional filters"""
    query = db.query(Note).filter(Note.user_id == current_user.id)
    
    if workspace_id:
        query = query.filter(Note.workspace_id == workspace_id)
    if favorite is not None:
        query = query.filter(Note.is_favorite == favorite)
    
    notes = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {"total": total, "notes": notes}

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get note by ID"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note

@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: UUID,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update note"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for key, value in note_update.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete note"""
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}