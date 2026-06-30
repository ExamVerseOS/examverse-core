"""User domain models for the ExamVerseOS ecosystem."""

from __future__ import annotations

import enum

from pydantic import EmailStr, Field

from examverse_core.models.base import BaseEntity, BaseReadModel


class UserRole(str, enum.Enum):
    """Supported user roles across the ExamVerse platform."""

    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    MODERATOR = "moderator"
    GUEST = "guest"


class UserStatus(str, enum.Enum):
    """Account lifecycle states for a user."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    DELETED = "deleted"


class UserPreferences(BaseEntity):
    """User-specific application preferences.

    Attributes:
        user_id: Foreign key to the owning user.
        language: BCP-47 language code (e.g. ``"en"``).
        timezone: IANA timezone string.
        notifications_enabled: Global notification opt-in flag.
        daily_goal_minutes: Target daily study duration in minutes.
        theme: UI theme preference (e.g. ``"dark"`` / ``"light"``).
    """

    user_id: str
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="UTC", max_length=64)
    notifications_enabled: bool = True
    daily_goal_minutes: int = Field(default=30, ge=0, le=1440)
    theme: str = Field(default="system", max_length=20)


class User(BaseEntity):
    """Core user entity representing any person in the ExamVerse ecosystem.

    Attributes:
        email: Verified email address.
        username: URL-safe unique display name.
        full_name: Display name.
        role: Primary access role.
        status: Account lifecycle state.
        avatar_url: Optional URL to the user's profile image.
        bio: Optional short biography.
        is_email_verified: Whether the email address has been confirmed.
        hashed_password: Argon2/bcrypt hash of the user's password.
        preferences: Embedded user preferences.
    """

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-z0-9_-]+$")
    full_name: str = Field(..., min_length=1, max_length=200)
    role: UserRole = UserRole.STUDENT
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    avatar_url: str | None = None
    bio: str | None = Field(default=None, max_length=500)
    is_email_verified: bool = False
    hashed_password: str = Field(..., description="Argon2/bcrypt password hash")

    @property
    def is_active(self) -> bool:
        """True when the account status is ACTIVE.

        Returns:
            Boolean indicating active status.
        """
        return self.status == UserStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        """True when the user holds the ADMIN role.

        Returns:
            Boolean indicating admin role.
        """
        return self.role == UserRole.ADMIN


class UserSummary(BaseReadModel):
    """Lightweight read projection of a user for list views.

    Attributes:
        id: Entity ID.
        username: Display username.
        full_name: Display full name.
        avatar_url: Optional profile picture URL.
        role: Primary role.
        status: Account status.
    """

    id: str
    username: str
    full_name: str
    avatar_url: str | None
    role: UserRole
    status: UserStatus
