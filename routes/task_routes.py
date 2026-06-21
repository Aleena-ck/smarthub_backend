from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from models.task_model import Task
from models.workspace_model import Workspace
from models.user_model import User
from schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse, TaskStatus
from middleware.auth_middleware import get_current_user
from uuid import UUID
from typing import Optional

router = APIRouter()
# backend/routes/task_routes.py

# backend/routes/task_routes.py - Add this before the other routes

@router.get("/")
def get_tasks(
    workspace_id: Optional[UUID] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get tasks with optional filters"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if workspace_id:
        query = query.filter(Task.workspace_id == workspace_id)
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {"total": total, "tasks": tasks}

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    workspace = db.query(Workspace).filter(
        Workspace.id == task.workspace_id,
        Workspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # ✅ Use deadline (not due_date)
    db_task = Task(
        user_id=current_user.id,
        workspace_id=task.workspace_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        deadline=task.deadline,  # ← Changed from due_date
        reminder_enabled=task.reminder_at is not None,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # ✅ Update fields
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.deadline is not None:  # ← Changed from due_date
        task.deadline = task_update.deadline
    if task_update.reminder_at is not None:
        task.reminder_at = task_update.reminder_at
    
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # ✅ Map deadline to due_date for response
    response_data = {
        "id": task.id,
        "workspace_id": task.workspace_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "deadline": task.deadline,  # ← Changed from due_date
        "reminder_at": task.reminder_at,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    return response_data