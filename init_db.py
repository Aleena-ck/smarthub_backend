#!/usr/bin/env python
"""Database initialization script"""

from database.connection import engine, Base
from models import (
    User, Workspace, Task, Note, Document, AIChat, DeviceToken,
    CalendarEvent, FocusSession, Achievement, UserFocusStats
)

def init_db():
    """Create all database tables"""
    print("🔵 Creating database tables...")
    try:
        # Drop existing tables (comment this line if you want to keep data)
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        print("   - users")
        print("   - workspaces")
        print("   - tasks")
        print("   - notes")
        print("   - documents")
        print("   - ai_chats")
        print("   - device_tokens")
        print("   - calendar_events")
        print("   - focus_sessions")
        print("   - achievements")
        print("   - user_focus_stats")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    return True

if __name__ == "__main__":
    init_db()