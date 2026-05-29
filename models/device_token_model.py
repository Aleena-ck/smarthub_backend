from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class DeviceToken(Base):
    __tablename__ = "device_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    device_type = Column(String, default="android")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())