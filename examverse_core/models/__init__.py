"""ExamVerse shared domain models."""

from examverse_core.models.ai import (
    AIRequest,
    Conversation,
    ConversationMessage,
    ConversationStatus,
    MessageRole,
    Notification,
)
from examverse_core.models.analytics import AnalyticsEvent, Settings
from examverse_core.models.base import BaseEntity, BaseReadModel, BaseValueObject
from examverse_core.models.exam import (
    Book,
    DifficultyLevel,
    Exam,
    ExamStatus,
    ExamSummary,
    Option,
    PYQ,
    Question,
    QuestionType,
    Subject,
    Topic,
)
from examverse_core.models.study import (
    Flashcard,
    LearningPath,
    Progress,
    Revision,
    RevisionStage,
    SessionStatus,
    StudySession,
)
from examverse_core.models.user import (
    User,
    UserPreferences,
    UserRole,
    UserStatus,
    UserSummary,
)

__all__ = [
    "BaseEntity",
    "BaseReadModel",
    "BaseValueObject",
    "User",
    "UserRole",
    "UserStatus",
    "UserPreferences",
    "UserSummary",
    "Subject",
    "Topic",
    "Question",
    "QuestionType",
    "DifficultyLevel",
    "Option",
    "PYQ",
    "Book",
    "Exam",
    "ExamStatus",
    "ExamSummary",
    "Flashcard",
    "RevisionStage",
    "StudySession",
    "SessionStatus",
    "Revision",
    "Progress",
    "LearningPath",
    "Conversation",
    "ConversationStatus",
    "ConversationMessage",
    "MessageRole",
    "AIRequest",
    "Notification",
    "AnalyticsEvent",
    "Settings",
]
