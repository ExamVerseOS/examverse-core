"""Reusable domain validators for the ExamVerseOS ecosystem.

All validators are stateless callables or Pydantic annotated types that
can be composed into any model or called standalone.

Example:
    >>> validate_email("user@examverse.io")
    'user@examverse.io'
    >>> validate_slug("my-topic")
    'my-topic'
"""

from __future__ import annotations

import re
import uuid as _uuid
from typing import Annotated

from email_validator import EmailNotValidError, validate_email as _validate_email
from pydantic import AfterValidator


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------


def validate_email(value: str) -> str:
    """Validate and normalise an email address.

    Args:
        value: Raw email string to validate.

    Returns:
        The normalised email address.

    Raises:
        ValueError: If the email address is not valid.
    """
    try:
        info = _validate_email(value, check_deliverability=False)
        return info.normalized
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc


EmailField = Annotated[str, AfterValidator(validate_email)]
"""Pydantic-compatible email annotation that applies :func:`validate_email`."""


# ---------------------------------------------------------------------------
# Slug
# ---------------------------------------------------------------------------

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_slug(value: str, *, max_length: int = 100) -> str:
    """Validate a URL-safe slug.

    A valid slug contains only lowercase alphanumeric characters and
    hyphens, does not start or end with a hyphen, and has no consecutive
    hyphens.

    Args:
        value: The slug to validate.
        max_length: Maximum allowed slug length.

    Returns:
        The slug unchanged if valid.

    Raises:
        ValueError: If the slug is invalid.
    """
    if not value:
        raise ValueError("Slug must not be empty.")
    if len(value) > max_length:
        raise ValueError(f"Slug must not exceed {max_length} characters.")
    if not _SLUG_RE.match(value):
        raise ValueError(
            "Slug must contain only lowercase letters, digits, and hyphens, "
            "and must not start or end with a hyphen."
        )
    return value


SlugField = Annotated[str, AfterValidator(validate_slug)]
"""Pydantic-compatible slug annotation."""


# ---------------------------------------------------------------------------
# UUID
# ---------------------------------------------------------------------------


def validate_uuid(value: str, *, version: int = 4) -> str:
    """Validate a UUID string.

    Args:
        value: The UUID string to validate.
        version: Expected UUID version (default: 4).

    Returns:
        The UUID string in canonical lowercase form.

    Raises:
        ValueError: If the string is not a valid UUID of the expected version.
    """
    try:
        parsed = _uuid.UUID(value, version=version)
        return str(parsed)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid UUID v{version}: {value!r}") from exc


UUIDField = Annotated[str, AfterValidator(validate_uuid)]
"""Pydantic-compatible UUID v4 annotation."""


# ---------------------------------------------------------------------------
# Topic and Exam Codes
# ---------------------------------------------------------------------------

_CODE_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,29}$")


def validate_code(value: str, *, label: str = "Code") -> str:
    """Validate an uppercase topic or exam code.

    Valid codes start with an uppercase letter and contain only uppercase
    letters, digits, and underscores (2–30 characters total).

    Args:
        value: The code string to validate.
        label: Human-readable field label for error messages.

    Returns:
        The code unchanged if valid.

    Raises:
        ValueError: If the code format is invalid.
    """
    if not _CODE_RE.match(value):
        raise ValueError(
            f"{label} must start with an uppercase letter and contain only "
            "uppercase letters, digits, and underscores (2–30 characters)."
        )
    return value


# ---------------------------------------------------------------------------
# URL
# ---------------------------------------------------------------------------

_URL_RE = re.compile(
    r"^https?://"
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
    r"localhost|"
    r"\d{1,3}(?:\.\d{1,3}){3})"
    r"(?::\d+)?"
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_url(value: str) -> str:
    """Validate an HTTP or HTTPS URL.

    Args:
        value: The URL string to validate.

    Returns:
        The URL unchanged if valid.

    Raises:
        ValueError: If the URL is not a valid HTTP/HTTPS URL.
    """
    if not _URL_RE.match(value):
        raise ValueError(f"Invalid URL: {value!r}")
    return value


URLField = Annotated[str, AfterValidator(validate_url)]
"""Pydantic-compatible HTTP/HTTPS URL annotation."""


# ---------------------------------------------------------------------------
# Filename
# ---------------------------------------------------------------------------

_SAFE_FILENAME_RE = re.compile(r"^[\w\-. ]+$")
_DANGEROUS_EXTENSIONS = frozenset(
    {".exe", ".bat", ".sh", ".ps1", ".cmd", ".com", ".scr", ".php", ".py"}
)


def validate_filename(value: str) -> str:
    """Validate a file upload filename for safety.

    Args:
        value: The filename to validate.

    Returns:
        The filename unchanged if safe.

    Raises:
        ValueError: If the filename contains unsafe characters or a
            dangerous extension.
    """
    if not value or not value.strip():
        raise ValueError("Filename must not be empty.")
    if not _SAFE_FILENAME_RE.match(value):
        raise ValueError(
            "Filename contains unsafe characters. "
            "Only letters, digits, spaces, hyphens, underscores, and dots are allowed."
        )
    ext = "." + value.rsplit(".", 1)[-1].lower() if "." in value else ""
    if ext in _DANGEROUS_EXTENSIONS:
        raise ValueError(f"File extension {ext!r} is not permitted.")
    return value


# ---------------------------------------------------------------------------
# Phone (basic E.164)
# ---------------------------------------------------------------------------

_E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")


def validate_phone(value: str) -> str:
    """Validate a phone number in E.164 format.

    Args:
        value: The phone number to validate (must start with ``+``).

    Returns:
        The phone number unchanged if valid.

    Raises:
        ValueError: If the format is not E.164-compliant.
    """
    if not _E164_RE.match(value):
        raise ValueError(
            "Phone number must be in E.164 format (e.g. +919876543210)."
        )
    return value
