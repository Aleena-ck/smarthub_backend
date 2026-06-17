from services.ollama_service import OllamaService
from sqlalchemy.orm import Session
from models.ai_chat_model import AIChat
from models.task_model import Task
from models.note_model import Note
from uuid import UUID
from datetime import datetime, timedelta

class AIService:
    """Service for AI-related operations"""
    
    def __init__(self):
        self.ollama = OllamaService()
    
    async def chat(self, db: Session, user_id: UUID, prompt: str, workspace_id: UUID = None, chat_id: UUID = None) -> tuple[str, UUID]:
        """Handle chat with AI, maintaining context"""
        
        # Get or create chat session
        if chat_id:
            chat = db.query(AIChat).filter(
                AIChat.id == chat_id,
                AIChat.user_id == user_id
            ).first()
        else:
            chat = None
        
        if not chat:
            chat = AIChat(
                user_id=user_id,
                workspace_id=workspace_id,
                title=prompt[:50],
                messages=[]
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
        
        # Build context from previous messages
        context = ""
        if chat.messages:
            last_messages = chat.messages[-4:]  # Last 4 messages for context
            for msg in last_messages:
                context += f"{msg['role']}: {msg['content']}\n"
        
        # Add workspace context if provided
        workspace_context = ""
        if workspace_id:
            # Get recent tasks and notes from workspace
            recent_tasks = db.query(Task).filter(
                Task.workspace_id == workspace_id,
                Task.status != "completed"
            ).limit(5).all()
            
            recent_notes = db.query(Note).filter(
                Note.workspace_id == workspace_id
            ).order_by(Note.updated_at.desc()).limit(3).all()
            
            if recent_tasks or recent_notes:
                workspace_context = "\nWorkspace Context:\n"
                if recent_tasks:
                    workspace_context += "Recent Tasks:\n"
                    for task in recent_tasks:
                        workspace_context += f"- {task.title} (Priority: {task.priority.value})\n"
                if recent_notes:
                    workspace_context += "\nRecent Notes:\n"
                    for note in recent_notes:
                        workspace_context += f"- {note.title}\n"
        
        full_context = context + workspace_context
        
        # Get AI response
        ai_response = await self.ollama.generate(prompt, full_context)
        
        # Save messages
        messages = chat.messages or []
        messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.utcnow().isoformat()
        })
        messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        chat.messages = messages
        db.commit()
        
        return ai_response, chat.id
    
    async def get_daily_insight(self, db: Session, user_id: UUID) -> str:
        """Generate daily productivity insight"""
        # Get today's tasks
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        pending_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "pending"
        ).count()
        
        completed_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "completed",
            Task.updated_at >= today
        ).count()
        
        due_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.due_date <= tomorrow,
            Task.due_date >= today,
            Task.status != "completed"
        ).count()
        
        prompt = f"""Generate a short, encouraging daily productivity insight for a user with:
        - {pending_tasks} pending tasks
        - {completed_tasks} tasks completed today
        - {due_tasks} tasks due today
        
        Keep response under 150 characters, be positive and actionable."""
        
        return await self.ollama.generate(prompt)
    
    async def get_weekly_report(self, db: Session, user_id: UUID) -> str:
        """Generate weekly productivity report"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        completed_this_week = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "completed",
            Task.updated_at >= week_ago
        ).count()
        
        created_this_week = db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= week_ago
        ).count()
        
        notes_created = db.query(Note).filter(
            Note.user_id == user_id,
            Note.created_at >= week_ago
        ).count()
        
        prompt = f"""Generate a brief weekly productivity report summary:
        - Tasks completed: {completed_this_week}
        - Tasks created: {created_this_week}
        - Notes created: {notes_created}
        
        Keep response under 200 characters, be encouraging and provide 1 tip."""
        
        return await self.ollama.generate(prompt)
    
    # services/ollama_service.py - Add this method

async def generate_stream(self, prompt: str, context: str = None):
    """Stream response token by token"""
    full_prompt = prompt
    if context:
        full_prompt = f"Context: {context}\n\nUser: {prompt}\n\nAssistant:"
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        yield data.get("response", "")
    except Exception as e:
        yield f"Error: {str(e)}"