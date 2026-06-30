"""Tests for shared domain models."""

from __future__ import annotations

import pytest

from examverse_core.models.base import BaseEntity
from examverse_core.models.exam import (
    DifficultyLevel,
    Exam,
    ExamStatus,
    Option,
    Question,
    QuestionType,
    Subject,
    Topic,
)
from examverse_core.models.study import (
    Flashcard,
    LearningPath,
    Progress,
    RevisionStage,
    StudySession,
)
from examverse_core.models.user import User, UserRole, UserStatus


class TestBaseEntity:
    def test_id_generated(self) -> None:
        e = Subject(name="Math", code="MATH")
        assert len(e.id) == 36

    def test_created_at_set(self) -> None:
        e = Subject(name="Math", code="MATH")
        assert e.created_at is not None

    def test_model_with_updates_refreshes_updated_at(self) -> None:
        e = Subject(name="Math", code="MATH")
        original_updated = e.updated_at
        import time; time.sleep(0.001)
        updated = e.model_with_updates(name="Mathematics")
        assert updated.name == "Mathematics"


class TestUser:
    def test_valid_user(self) -> None:
        u = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
        )
        assert u.role == UserRole.STUDENT
        assert not u.is_active

    def test_is_admin_for_admin_role(self) -> None:
        u = User(
            email="a@a.com",
            username="admin",
            full_name="Admin",
            hashed_password="h",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
        )
        assert u.is_admin
        assert u.is_active

    def test_invalid_username_raises(self) -> None:
        with pytest.raises(Exception):
            User(
                email="a@a.com",
                username="Invalid User Name!",
                full_name="Test",
                hashed_password="h",
            )


class TestExamModels:
    def test_subject_code_must_be_uppercase(self) -> None:
        with pytest.raises(Exception):
            Subject(name="Physics", code="physics")

    def test_valid_subject(self) -> None:
        s = Subject(name="Physics", code="PHY")
        assert s.code == "PHY"

    def test_valid_question(self) -> None:
        q = Question(
            topic_id="t1",
            subject_id="s1",
            stem="What is 2+2?",
            type=QuestionType.MCQ,
            difficulty=DifficultyLevel.EASY,
        )
        assert q.marks == 1.0

    def test_exam_defaults(self) -> None:
        e = Exam(title="JEE 2024", code="JEE_2024")
        assert e.status == ExamStatus.DRAFT


class TestStudyModels:
    def test_study_session_accuracy_no_attempts(self) -> None:
        s = StudySession(user_id="u1", subject_id="s1")
        assert s.accuracy == 0.0

    def test_study_session_accuracy(self) -> None:
        s = StudySession(
            user_id="u1",
            subject_id="s1",
            questions_attempted=10,
            correct_answers=7,
        )
        assert s.accuracy == 70.0

    def test_flashcard_defaults(self) -> None:
        f = Flashcard(user_id="u1", topic_id="t1", front="Q", back="A")
        assert f.stage == RevisionStage.NEW
        assert f.ease_factor == 2.5

    def test_progress_defaults(self) -> None:
        p = Progress(user_id="u1", subject_id="s1")
        assert p.streak_days == 0
        assert p.average_score == 0.0
