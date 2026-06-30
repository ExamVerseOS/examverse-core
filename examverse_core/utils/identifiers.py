"""Identifier generation utilities for the ExamVerseOS platform.

Provides deterministic and random ID generators for various entity types.

Example:
    >>> generate_id()
    '018f1a2b-3c4d-7e8f-9012-3456789abcde'
    >>> generate_short_id()
    'k5j2hq'
"""

from __future__ import annotations

import hashlib
import uuid


def generate_id() -> str:
    """Generate a random UUID v4 identifier.

    Returns:
        A lowercase UUID v4 string.
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short URL-safe random identifier.

    Uses the first ``length`` characters of a URL-safe UUID hex string.

    Args:
        length: Desired identifier length (default: 8, max: 32).

    Returns:
        A lowercase alphanumeric string of the requested length.
    """
    length = min(max(length, 4), 32)
    return uuid.uuid4().hex[:length]


def generate_namespaced_id(namespace: str, name: str) -> str:
    """Generate a deterministic UUID v5 from a namespace and name.

    Useful for creating stable identifiers from external data (e.g. exam
    codes, ISBN numbers) so the same input always produces the same ID.

    Args:
        namespace: A namespace discriminator string (e.g. ``"exam"``).
        name: The distinguishing name within the namespace.

    Returns:
        A UUID v5 string derived from the inputs.
    """
    ns_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, namespace)
    return str(uuid.uuid5(ns_uuid, name))


def generate_correlation_id() -> str:
    """Generate a new correlation ID for distributed tracing.

    Returns:
        A UUID v4 string.
    """
    return str(uuid.uuid4())


def content_hash(data: str | bytes) -> str:
    """Compute a stable SHA-256 content hash for deduplication.

    Args:
        data: The content to hash.

    Returns:
        Lowercase hexadecimal SHA-256 digest.
    """
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()
