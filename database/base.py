# database/base.py
from database.connection import Base
from models.user_model import User
# Import all models here so Alembic can detect them
from models.task_model import Task
from models.notification_model import Notification
from models.document_model import Document