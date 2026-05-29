from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.user_model import User
from models.task_model import Task
from models.note_model import Note
from middleware.auth_middleware import get_current_user
from uuid import UUID

router = APIRouter()

@router.get("/")
def search(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search across user's content"""
    search_term = f"%{q}%"
    
    # Search tasks
    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.title.ilike(search_term)
    ).limit(10).all()
    
    # Search notes
    notes = db.query(Note).filter(
        Note.user_id == current_user.id,
        Note.title.ilike(search_term)
    ).limit(10).all()
    
    # Format results
    results = []
    
    for task in tasks:
        results.append({
            "type": "task",
            "id": str(task.id),
            "title": task.title,
            "workspace_id": str(task.workspace_id),
            "status": task.status.value
        })
    
    for note in notes:
        results.append({
            "type": "note",
            "id": str(note.id),
            "title": note.title,
            "workspace_id": str(note.workspace_id),
            "is_favorite": note.is_favorite
        })
    
    return {"query": q, "total": len(results), "results": results}