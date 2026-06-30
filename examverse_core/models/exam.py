"""Exam domain models — exams, subjects, topics, questions, and PYQs."""

from __future__ import annotations

import enum
from typing import Any

from pydantic import Field

from examverse_core.models.base import BaseEntity, BaseReadModel


class DifficultyLevel(str, enum.Enum):
    """Question or exam difficulty tier."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class QuestionType(str, enum.Enum):
    """Supported question formats."""

    MCQ = "mcq"
    MSQ = "msq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    FILL_IN_BLANK = "fill_in_blank"
    MATCH_COLUMNS = "match_columns"
    NUMERICAL = "numerical"


class ExamStatus(str, enum.Enum):
    """Publication lifecycle of an exam."""

    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Subject(BaseEntity):
    """An academic subject grouping related topics.

    Attributes:
        name: Human-readable subject name.
        code: Short uppercase code (e.g. ``"PHY"``, ``"MATH"``).
        description: Optional extended description.
        icon_url: Optional icon image URL.
        is_active: Whether this subject is publicly visible.
    """

    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=2, max_length=20, pattern=r"^[A-Z0-9_]+$")
    description: str | None = Field(default=None, max_length=2000)
    icon_url: str | None = None
    is_active: bool = True


class Topic(BaseEntity):
    """A discrete study topic within a subject.

    Attributes:
        subject_id: Parent subject identifier.
        name: Topic name.
        code: Unique topic code within the subject.
        description: Optional extended description.
        weight: Importance weight (0.0–1.0) within the subject.
        order: Display ordering index.
    """

    subject_id: str
    name: str = Field(..., min_length=1, max_length=300)
    code: str = Field(..., min_length=2, max_length=30, pattern=r"^[A-Z0-9_]+$")
    description: str | None = Field(default=None, max_length=2000)
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    order: int = Field(default=0, ge=0)


class Option(BaseEntity):
    """A single answer option for MCQ/MSQ questions.

    Attributes:
        text: The option text displayed to the student.
        is_correct: Whether this option is a correct answer.
        explanation: Optional per-option explanation.
    """

    text: str = Field(..., min_length=1, max_length=1000)
    is_correct: bool = False
    explanation: str | None = Field(default=None, max_length=2000)


class Question(BaseEntity):
    """A single exam question with all metadata.

    Attributes:
        topic_id: Associated topic identifier.
        subject_id: Denormalised subject identifier for fast filtering.
        type: Question format type.
        difficulty: Difficulty level.
        stem: The question text (HTML-safe markdown).
        options: Answer options (empty for open-ended types).
        correct_answer: Model answer text for open-ended types.
        explanation: Solution explanation.
        marks: Marks awarded for a correct answer.
        negative_marks: Marks deducted for an incorrect answer.
        tags: Searchable labels.
        source: Citation or original source reference.
        is_active: Whether the question is available for use.
        metadata: Arbitrary extension fields.
    """

    topic_id: str
    subject_id: str
    type: QuestionType = QuestionType.MCQ
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    stem: str = Field(..., min_length=1, max_length=5000)
    options: list[Option] = Field(default_factory=list)
    correct_answer: str | None = Field(default=None, max_length=5000)
    explanation: str | None = Field(default=None, max_length=5000)
    marks: float = Field(default=1.0, ge=0.0)
    negative_marks: float = Field(default=0.0, ge=0.0)
    tags: list[str] = Field(default_factory=list)
    source: str | None = None
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PYQ(BaseEntity):
    """Previous Year Question — an official past exam question.

    Attributes:
        question_id: Reference to the canonical :class:`Question`.
        exam_name: Name of the exam this question appeared in.
        exam_code: Standardised exam code (e.g. ``"JEE_ADV_2023"``).
        year: Year the question appeared.
        paper_code: Sub-paper identifier (e.g. ``"PAPER_1"``).
        shift: Exam shift (e.g. ``"MORNING"``, ``"EVENING"``).
    """

    question_id: str
    exam_name: str = Field(..., max_length=200)
    exam_code: str = Field(..., max_length=50, pattern=r"^[A-Z0-9_]+$")
    year: int = Field(..., ge=1900, le=2100)
    paper_code: str | None = None
    shift: str | None = None


class Book(BaseEntity):
    """Reference book metadata used in the ExamVerse content library.

    Attributes:
        title: Book title.
        authors: List of author names.
        isbn: Optional ISBN-13.
        subject_ids: Subjects this book covers.
        edition: Edition label.
        publisher: Publisher name.
        cover_url: Optional cover image URL.
    """

    title: str = Field(..., min_length=1, max_length=500)
    authors: list[str] = Field(default_factory=list)
    isbn: str | None = Field(default=None, max_length=20)
    subject_ids: list[str] = Field(default_factory=list)
    edition: str | None = None
    publisher: str | None = None
    cover_url: str | None = None


class Exam(BaseEntity):
    """A published exam consisting of sections with questions.

    Attributes:
        title: Exam title.
        code: Unique exam code (e.g. ``"JEE_ADV_2024"``).
        description: Optional extended description.
        status: Publication lifecycle state.
        subject_ids: Subjects covered.
        total_marks: Total available marks.
        duration_minutes: Exam duration.
        instructions: Student-facing instructions (markdown).
        metadata: Arbitrary extension fields.
    """

    title: str = Field(..., min_length=1, max_length=500)
    code: str = Field(..., max_length=50, pattern=r"^[A-Z0-9_]+$")
    description: str | None = Field(default=None, max_length=5000)
    status: ExamStatus = ExamStatus.DRAFT
    subject_ids: list[str] = Field(default_factory=list)
    total_marks: float = Field(default=0.0, ge=0.0)
    duration_minutes: int = Field(default=180, ge=1)
    instructions: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExamSummary(BaseReadModel):
    """Lightweight read projection for exam list views.

    Attributes:
        id: Entity ID.
        title: Exam title.
        code: Exam code.
        status: Current status.
        total_marks: Total marks.
        duration_minutes: Duration in minutes.
    """

    id: str
    title: str
    code: str
    status: ExamStatus
    total_marks: float
    duration_minutes: int
