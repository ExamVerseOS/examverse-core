"""Role-based permission model for ExamVerseOS.

Provides :class:`Permission`, :class:`Role`, and :class:`PermissionChecker`
as reusable building blocks. Actual enforcement is done by downstream
services — this module defines the model only.

Example:
    >>> checker = PermissionChecker()
    >>> checker.has_permission(UserRole.ADMIN, Permission.DELETE_QUESTION)
    True
"""

from __future__ import annotations

import enum

from pydantic import BaseModel, Field

from examverse_core.models.user import UserRole


class Permission(str, enum.Enum):
    """Granular permissions across the ExamVerseOS platform."""

    READ_EXAM = "exam:read"
    CREATE_EXAM = "exam:create"
    UPDATE_EXAM = "exam:update"
    DELETE_EXAM = "exam:delete"
    PUBLISH_EXAM = "exam:publish"

    READ_QUESTION = "question:read"
    CREATE_QUESTION = "question:create"
    UPDATE_QUESTION = "question:update"
    DELETE_QUESTION = "question:delete"

    READ_USER = "user:read"
    CREATE_USER = "user:create"
    UPDATE_USER = "user:update"
    DELETE_USER = "user:delete"
    MANAGE_ROLES = "user:manage_roles"

    READ_ANALYTICS = "analytics:read"
    EXPORT_ANALYTICS = "analytics:export"

    USE_AI = "ai:use"
    MANAGE_AI_PROVIDERS = "ai:manage_providers"

    MANAGE_PLUGINS = "plugin:manage"
    MANAGE_SETTINGS = "settings:manage"

    MODERATE_CONTENT = "content:moderate"


_ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.GUEST: frozenset({
        Permission.READ_EXAM,
        Permission.READ_QUESTION,
    }),
    UserRole.STUDENT: frozenset({
        Permission.READ_EXAM,
        Permission.READ_QUESTION,
        Permission.USE_AI,
    }),
    UserRole.TEACHER: frozenset({
        Permission.READ_EXAM,
        Permission.CREATE_EXAM,
        Permission.UPDATE_EXAM,
        Permission.READ_QUESTION,
        Permission.CREATE_QUESTION,
        Permission.UPDATE_QUESTION,
        Permission.USE_AI,
        Permission.READ_ANALYTICS,
    }),
    UserRole.MODERATOR: frozenset({
        Permission.READ_EXAM,
        Permission.UPDATE_EXAM,
        Permission.READ_QUESTION,
        Permission.UPDATE_QUESTION,
        Permission.DELETE_QUESTION,
        Permission.MODERATE_CONTENT,
        Permission.READ_ANALYTICS,
        Permission.USE_AI,
    }),
    UserRole.ADMIN: frozenset(Permission),
}


class RoleDefinition(BaseModel):
    """Descriptor for a role and its associated permissions.

    Attributes:
        role: The user role.
        permissions: Set of permissions granted to this role.
        description: Human-readable description of the role.
    """

    role: UserRole
    permissions: frozenset[Permission]
    description: str = Field(default="", max_length=500)

    model_config = {"arbitrary_types_allowed": True}


class PermissionChecker:
    """Stateless permission evaluation engine.

    Uses the built-in role→permission map by default. Pass a custom mapping
    to override the defaults for your service.

    Args:
        role_permissions: Override the default role-to-permission mapping.
    """

    def __init__(
        self,
        role_permissions: dict[UserRole, frozenset[Permission]] | None = None,
    ) -> None:
        self._map: dict[UserRole, frozenset[Permission]] = role_permissions or _ROLE_PERMISSIONS

    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """Check whether a role holds a specific permission.

        Args:
            role: The user's role.
            permission: The permission to check.

        Returns:
            ``True`` if the role has the permission, ``False`` otherwise.
        """
        return permission in self._map.get(role, frozenset())

    def has_any_permission(self, role: UserRole, *permissions: Permission) -> bool:
        """Check whether a role holds at least one of the given permissions.

        Args:
            role: The user's role.
            *permissions: One or more permissions to check.

        Returns:
            ``True`` if the role has any of the listed permissions.
        """
        granted = self._map.get(role, frozenset())
        return any(p in granted for p in permissions)

    def has_all_permissions(self, role: UserRole, *permissions: Permission) -> bool:
        """Check whether a role holds all of the given permissions.

        Args:
            role: The user's role.
            *permissions: Permissions that must all be held.

        Returns:
            ``True`` if the role holds every listed permission.
        """
        granted = self._map.get(role, frozenset())
        return all(p in granted for p in permissions)

    def get_permissions(self, role: UserRole) -> frozenset[Permission]:
        """Return all permissions granted to a role.

        Args:
            role: The user's role.

        Returns:
            Frozenset of :class:`Permission` values.
        """
        return self._map.get(role, frozenset())
