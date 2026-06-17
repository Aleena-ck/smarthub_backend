from schemas.user_schema import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate, PasswordChange
from schemas.workspace_schema import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse
from schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from schemas.note_schema import NoteCreate, NoteUpdate, NoteResponse
from schemas.document_schema import DocumentResponse, DocumentUploadResponse
from schemas.ai_chat_schema import ChatRequest, ChatResponse, AIChatCreate, AIChatResponse, AIChatMessage
from schemas.calendar_schema import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse, NotificationMode, RecurrenceRule
from schemas.focus_schema import FocusSessionCreate, FocusSessionComplete, FocusSessionResponse, FocusStatus
from schemas.dashboard_schema import DashboardResponse, TodayItem, RecentActivityItem, FutureActivityItem, AchievementItem, DashboardCounters