from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from models.workspace_model import Workspace
from models.user_model import User
from schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from middleware.auth_middleware import get_current_user
from services.ai_service import AIService
from uuid import UUID
from datetime import datetime

router = APIRouter()
ai_service = AIService()

@router.get("/", response_model=list[WorkspaceResponse])
def get_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all workspaces for current user"""
    workspaces = db.query(Workspace).filter(
        Workspace.user_id == current_user.id
    ).order_by(Workspace.created_at).all()
    
    # Fix: Ensure updated_at is not None
    for workspace in workspaces:
        if workspace.updated_at is None:
            workspace.updated_at = workspace.created_at
    
    return workspaces

@router.post("/", response_model=WorkspaceResponse)
def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace"""
    now = datetime.utcnow()
    
    db_workspace = Workspace(
        **workspace.model_dump(),
        user_id=current_user.id,
        created_at=now,
        updated_at=now
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workspace by ID"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Fix: Ensure updated_at is not None
    if workspace.updated_at is None:
        workspace.updated_at = workspace.created_at
    
    return workspace

@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: UUID,
    workspace_update: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update workspace"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    for key, value in workspace_update.model_dump(exclude_unset=True).items():
        setattr(workspace, key, value)
    
    workspace.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(workspace)
    return workspace

@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete workspace"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    db.delete(workspace)
    db.commit()
    return {"message": "Workspace deleted successfully"}

@router.get("/{workspace_id}/summary")
async def get_workspace_summary(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI summary of workspace content"""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Get workspace stats
    from models.task_model import Task
    from models.note_model import Note
    
    task_count = db.query(Task).filter(Task.workspace_id == workspace_id).count()
    pending_tasks = db.query(Task).filter(
        Task.workspace_id == workspace_id,
        Task.status == "pending"
    ).count()
    note_count = db.query(Note).filter(Note.workspace_id == workspace_id).count()
    
    prompt = f"""Generate a brief summary for workspace "{workspace.name}":
    - Total tasks: {task_count}
    - Pending tasks: {pending_tasks}
    - Total notes: {note_count}
    
    Provide a 1-sentence summary and 1 actionable tip."""
    
    summary = await ai_service.ollama.generate(prompt)
    
    return {"summary": summary}