from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.connection import engine, Base
from routes import (
    auth_routes, workspace_routes, task_routes, note_routes,
    document_routes, ai_routes, notification_routes, search_routes
)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartHub API",
    description="AI-powered personal workspace API",
    version="1.0.0"
)

# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
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

@app.get("/")
def root():
    return {
        "message": "SmartHub API Running",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "workspaces": "/workspaces",
            "tasks": "/tasks",
            "notes": "/notes",
            "documents": "/documents",
            "ai": "/ai",
            "search": "/search"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 8000