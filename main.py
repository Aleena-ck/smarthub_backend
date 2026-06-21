from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database.connection import engine, Base
from routes import (
    auth_routes, workspace_routes, task_routes, note_routes,
    document_routes, ai_routes, notification_routes, search_routes,
    calendar_routes, focus_routes, dashboard_routes
)
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize connections (optional)
    try:
        from services.rabbitmq_service import get_rabbitmq_connection
        await get_rabbitmq_connection()
        logger.info("✅ RabbitMQ connected")
    except Exception as e:
        logger.warning(f"⚠️ RabbitMQ not available: {e}. Notifications will be disabled.")
    
    try:
        from services.redis_service import get_redis_client
        await get_redis_client()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}. Caching will be disabled.")
    
    yield
    
    # Shutdown: Close connections
    try:
        from services.rabbitmq_service import connection as rmq_conn
        if rmq_conn and not rmq_conn.is_closed:
            await rmq_conn.close()
    except:
        pass
    
    try:
        from services.redis_service import redis_client
        if redis_client:
            await redis_client.close()
    except:
        pass

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartHub API",
    description="AI-powered personal workspace API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(workspace_routes.router, prefix="/workspaces", tags=["Workspaces"])
app.include_router(task_routes.router, prefix="/tasks", tags=["Tasks"])
app.include_router(note_routes.router, prefix="/notes", tags=["Notes"])
app.include_router(document_routes.router, prefix="/documents", tags=["Documents"])
app.include_router(ai_routes.router, prefix="/ai", tags=["AI"])
app.include_router(notification_routes.router, prefix="/notifications", tags=["Notifications"])
app.include_router(search_routes.router, prefix="/search", tags=["Search"])
app.include_router(calendar_routes.router, prefix="/calendar", tags=["Calendar"])
app.include_router(focus_routes.router, prefix="/focus", tags=["Focus"])
app.include_router(dashboard_routes.router, prefix="/dashboard", tags=["Dashboard"])


@app.get("/")
def root():
    return {"message": "SmartHub API Running", "version": "2.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
#   .\venv\Scripts\Activate.ps1  
#   uvicorn main:app --reload --host 0.0.0.0 --port 8000

"""
# Show root folder + immediate subfolders with their files (no nested folders)
Get-ChildItem | ForEach-Object { 
    if ($_.PSIsContainer) {
        Write-Host "`n📁 $($_.Name)/" -ForegroundColor Cyan
        # Show only files in this folder (no subfolders)
        Get-ChildItem $_.FullName -File | ForEach-Object {
            Write-Host "  📄 $($_.Name)" -ForegroundColor Gray
        }
        # Count subfolders but don't show them
        $subFolderCount = (Get-ChildItem $_.FullName -Directory).Count
        if ($subFolderCount -gt 0) {
            Write-Host "  ... ($subFolderCount subfolders)" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "📄 $($_.Name)" -ForegroundColor White
    }
}"""