"""General-purpose hashing utilities for ExamVerseOS.

Example:
    >>> md5_hex("hello")
    '5d41402abc4b2a76b9719d911017c592'
"""

from __future__ import annotations

import hashlib
import hmac


def sha256_hex(data: str | bytes) -> str:
    """Compute the SHA-256 hex digest of a string or bytes.

    Args:
        data: The input to hash.

    Returns:
        64-character lowercase hexadecimal digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def sha512_hex(data: str | bytes) -> str:
    """Compute the SHA-512 hex digest of a string or bytes.

    Args:
        data: The input to hash.

    Returns:
        128-character lowercase hexadecimal digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha512(data).hexdigest()


def md5_hex(data: str | bytes) -> str:
    """Compute the MD5 hex digest of a string or bytes.

    **Warning:** MD5 is not cryptographically secure. Use only for
    checksums and non-security-critical deduplication.

    Args:
        data: The input to hash.

    Returns:
        32-character lowercase hexadecimal digest.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.md5(data).hexdigest()  # noqa: S324


def hmac_sha256_hex(key: str | bytes, message: str | bytes) -> str:
    """Compute an HMAC-SHA256 hex digest.

    Args:
        key: The HMAC key.
        message: The message to authenticate.

    Returns:
        64-character lowercase hexadecimal HMAC digest.
    """
    if isinstance(key, str):
        key = key.encode("utf-8")
    if isinstance(message, str):
        message = message.encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def file_hash(path: str, algorithm: str = "sha256") -> str:
    """Compute the hash of a file on disk.

    Args:
        path: Path to the file.
        algorithm: Hash algorithm name (default: ``"sha256"``).

    Returns:
        Lowercase hexadecimal digest.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the algorithm is not supported.
    """
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
