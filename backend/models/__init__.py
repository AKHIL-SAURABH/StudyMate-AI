"""StudyMate AI — Pydantic Models Package."""

from backend.models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserInDB,
)
from backend.models.subject import (
    SubjectCreate,
    SubjectResponse,
    TopicCreate,
    TopicResponse,
)
from backend.models.session import (
    StudySessionCreate,
    StudySessionResponse,
)
from backend.models.quiz import (
    QuizGenerateRequest,
    QuizQuestion,
    QuizResponse,
    QuizSubmitRequest,
    QuizScoreResponse,
)
from backend.models.chat import (
    ChatRequest,
    ChatResponse,
    AgentStep,
)
from backend.models.analytics import (
    ProgressOverview,
    StudyAnalytics,
    WeeklySummary,
)

__all__ = [
    "UserCreate", "UserLogin", "UserResponse", "UserInDB",
    "SubjectCreate", "SubjectResponse", "TopicCreate", "TopicResponse",
    "StudySessionCreate", "StudySessionResponse",
    "QuizGenerateRequest", "QuizQuestion", "QuizResponse",
    "QuizSubmitRequest", "QuizScoreResponse",
    "ChatRequest", "ChatResponse", "AgentStep",
    "ProgressOverview", "StudyAnalytics", "WeeklySummary",
]
