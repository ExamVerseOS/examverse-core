"""Tests for PermissionChecker."""

from __future__ import annotations

from examverse_core.models.user import UserRole
from examverse_core.security.permissions import Permission, PermissionChecker


class TestPermissionChecker:
    def test_admin_has_all_permissions(self) -> None:
        checker = PermissionChecker()
        for perm in Permission:
            assert checker.has_permission(UserRole.ADMIN, perm)

    def test_guest_has_limited_permissions(self) -> None:
        checker = PermissionChecker()
        assert checker.has_permission(UserRole.GUEST, Permission.READ_EXAM)
        assert not checker.has_permission(UserRole.GUEST, Permission.DELETE_EXAM)

    def test_student_can_use_ai(self) -> None:
        checker = PermissionChecker()
        assert checker.has_permission(UserRole.STUDENT, Permission.USE_AI)

    def test_has_any_permission(self) -> None:
        checker = PermissionChecker()
        assert checker.has_any_permission(
            UserRole.STUDENT,
            Permission.DELETE_EXAM,
            Permission.READ_EXAM,
        )

    def test_has_all_permissions_false(self) -> None:
        checker = PermissionChecker()
        assert not checker.has_all_permissions(
            UserRole.STUDENT,
            Permission.READ_EXAM,
            Permission.DELETE_EXAM,
        )

    def test_get_permissions_returns_frozenset(self) -> None:
        checker = PermissionChecker()
        perms = checker.get_permissions(UserRole.TEACHER)
        assert isinstance(perms, frozenset)
        assert Permission.CREATE_EXAM in perms
