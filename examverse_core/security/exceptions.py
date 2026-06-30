"""Security-related exceptions for the ExamVerse platform."""

from __future__ import annotations


class SecurityError(Exception):
    """Base class for all ExamVerse security errors."""


class TokenExpiredError(SecurityError):
    """Raised when a JWT access or refresh token has expired."""

    def __init__(self) -> None:
        super().__init__("Token has expired.")


class TokenDecodeError(SecurityError):
    """Raised when a JWT cannot be decoded or signature verification fails.

    Args:
        detail: The underlying error message from the JWT library.
    """

    def __init__(self, detail: str = "Invalid token.") -> None:
        super().__init__(f"Token decode error: {detail}")
        self.detail = detail


class PermissionDeniedError(SecurityError):
    """Raised when a user attempts an action they are not authorised for.

    Args:
        action: The action that was denied.
        resource: The resource the action was attempted on.
    """

    def __init__(self, action: str, resource: str = "") -> None:
        msg = f"Permission denied: {action}"
        if resource:
            msg += f" on {resource!r}"
        super().__init__(msg)
        self.action = action
        self.resource = resource


class EncryptionError(SecurityError):
    """Raised when encryption or decryption fails."""
