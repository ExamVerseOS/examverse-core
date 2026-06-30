"""Study domain models — sessions, flashcards, revisions, and learning paths."""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Any

from pydantic import Field

from examverse_core.models.base import BaseEntity


class SessionStatus(str, enum.Enum):
    """Lifecycle states for a study session."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class RevisionStage(str, enum.Enum):
    """Spaced repetition stage for a flashcard."""

    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    RELEARNING = "relearning"
    MASTERED = "mastered"


class Flashcard(BaseEntity):
    """A spaced-repetition flashcard for a study topic.

    Attributes:
        user_id: Owner of this flashcard.
        topic_id: Associated topic.
        front: Front-of-card content (question / term).
        back: Back-of-card content (answer / definition).
        stage: Current spaced-repetition stage.
        ease_factor: SM-2 ease factor (≥ 1.3).
        interval_days: Days until next review.
        next_review_at: Scheduled next review timestamp.
        review_count: Total number of times reviewed.
        metadata: Arbitrary extension fields.
    """

    user_id: str
    topic_id: str
    front: str = Field(..., min_length=1, max_length=2000)
    back: str = Field(..., min_length=1, max_length=2000)
    stage: RevisionStage = RevisionStage.NEW
    ease_factor: float = Field(default=2.5, ge=1.3)
    interval_days: int = Field(default=1, ge=0)
    next_review_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    review_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StudySession(BaseEntity):
    """A bounded period of study activity.

    Attributes:
        user_id: The studying user.
        subject_id: Primary subject studied.
        topic_ids: Specific topics covered during this session.
        status: Lifecycle state.
        started_at: Session start timestamp.
        ended_at: Session end timestamp (``None`` while active).
        duration_seconds: Elapsed time (populated on completion).
        questions_attempted: Total questions answered.
        correct_answers: Count of correct answers.
        score: Achieved score as a percentage (0.0–100.0).
        notes: Optional free-text session notes.
    """

    user_id: str
    subject_id: str
    topic_ids: list[str] = Field(default_factory=list)
    status: SessionStatus = SessionStatus.ACTIVE
    started_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    ended_at: datetime | None = None
    duration_seconds: int = Field(default=0, ge=0)
    questions_attempted: int = Field(default=0, ge=0)
    correct_answers: int = Field(default=0, ge=0)
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    notes: str | None = Field(default=None, max_length=5000)

    @property
    def accuracy(self) -> float:
        """Accuracy as a percentage (0.0–100.0).

        Returns:
            Percentage of correct answers, or 0.0 if none attempted.
        """
        if self.questions_attempted == 0:
            return 0.0
        return round((self.correct_answers / self.questions_attempted) * 100, 2)


class Revision(BaseEntity):
    """A single revision attempt on a flashcard or question.

    Attributes:
        user_id: The revising user.
        flashcard_id: The flashcard being reviewed (if applicable).
        question_id: The question being reviewed (if applicable).
        rating: SM-2 quality rating (0 = complete blackout, 5 = perfect).
        time_taken_seconds: Time spent on this revision.
        is_correct: Whether the answer was correct.
    """

    user_id: str
    flashcard_id: str | None = None
    question_id: str | None = None
    rating: int = Field(..., ge=0, le=5, description="SM-2 quality rating")
    time_taken_seconds: int = Field(default=0, ge=0)
    is_correct: bool = False


class Progress(BaseEntity):
    """Aggregate progress record for a user on a subject.

    Attributes:
        user_id: The student.
        subject_id: The subject.
        topics_completed: IDs of fully mastered topics.
        total_study_minutes: Cumulative study time in minutes.
        average_score: Rolling average score percentage.
        streak_days: Current consecutive daily study streak.
        flashcards_mastered: Count of mastered flashcards.
        questions_seen: Total unique questions encountered.
    """

    user_id: str
    subject_id: str
    topics_completed: list[str] = Field(default_factory=list)
    total_study_minutes: int = Field(default=0, ge=0)
    average_score: float = Field(default=0.0, ge=0.0, le=100.0)
    streak_days: int = Field(default=0, ge=0)
    flashcards_mastered: int = Field(default=0, ge=0)
    questions_seen: int = Field(default=0, ge=0)


class LearningPath(BaseEntity):
    """An ordered curriculum of topics and resources for a learning goal.

    Attributes:
        user_id: The student this path is tailored for.
        title: Learning path name.
        goal: Short description of the learning objective.
        subject_ids: Subjects covered.
        topic_sequence: Ordered list of topic IDs to study.
        estimated_hours: Total estimated completion time.
        is_ai_generated: Whether this path was created by the AI engine.
        metadata: Arbitrary extension fields.
    """

    user_id: str
    title: str = Field(..., min_length=1, max_length=300)
    goal: str = Field(..., min_length=1, max_length=1000)
    subject_ids: list[str] = Field(default_factory=list)
    topic_sequence: list[str] = Field(default_factory=list)
    estimated_hours: float = Field(default=0.0, ge=0.0)
    is_ai_generated: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
