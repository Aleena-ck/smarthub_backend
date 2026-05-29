#!/usr/bin/env python
"""Database initialization script"""

from database.connection import engine, Base
from models import (
    User, Workspace, Task, Note, Document, AIChat, DeviceToken
)

def init_db():
    """Create all database tables"""
    print("🔵 Creating database tables...")
    try:
        Base.metadata.drop_all(bind=engine)  # Optional: drop existing tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        print("   - users")
        print("   - workspaces")
        print("   - tasks")
        print("   - notes")
        print("   - documents")
        print("   - ai_chats")
        print("   - device_tokens")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    return True

if __name__ == "__main__":
    init_db()