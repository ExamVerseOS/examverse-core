"""Cryptographic helper utilities for the ExamVerseOS platform.

Provides password hashing (bcrypt via passlib), symmetric encryption
(Fernet via cryptography), and general-purpose hashing utilities.
No authentication flow is implemented here.

Example:
    >>> hasher = PasswordHasher()
    >>> hashed = hasher.hash("my-secret-password")
    >>> hasher.verify("my-secret-password", hashed)
    True
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from base64 import urlsafe_b64decode, urlsafe_b64encode

from cryptography.fernet import Fernet, InvalidToken
from passlib.context import CryptContext

from examverse_core.security.exceptions import EncryptionError


class PasswordHasher:
    """Bcrypt password hashing and verification helper.

    Uses passlib's CryptContext so the hashing scheme can be upgraded
    without breaking existing hashes.
    """

    def __init__(self, schemes: list[str] | None = None) -> None:
        """Initialise with the given hashing schemes.

        Args:
            schemes: List of scheme names in passlib format.
                Defaults to ``["bcrypt"]`` with argon2 as a future-proof backup.
        """
        self._ctx = CryptContext(schemes=schemes or ["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        """Hash a plain-text password.

        Args:
            password: The plain-text password to hash.

        Returns:
            A bcrypt hash string.
        """
        return self._ctx.hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        """Verify a plain-text password against a stored hash.

        Args:
            plain: The plain-text password to check.
            hashed: The stored hash to compare against.

        Returns:
            ``True`` if the password matches, ``False`` otherwise.
        """
        return self._ctx.verify(plain, hashed)

    def needs_rehash(self, hashed: str) -> bool:
        """Check whether a hash needs to be upgraded to a newer scheme.

        Args:
            hashed: The stored hash to inspect.

        Returns:
            ``True`` if the hash should be regenerated.
        """
        return self._ctx.needs_update(hashed)


class SymmetricEncryption:
    """Fernet-based symmetric encryption for sensitive data at rest.

    Attributes:
        _fernet: The Fernet instance used for encryption/decryption.
    """

    def __init__(self, key: bytes | str) -> None:
        """Initialise with a Fernet-compatible key.

        Args:
            key: A 32-byte URL-safe base64-encoded key. Generate one with
                :meth:`generate_key`.

        Raises:
            EncryptionError: If the key is not valid Fernet format.
        """
        try:
            key_bytes = key.encode() if isinstance(key, str) else key
            self._fernet = Fernet(key_bytes)
        except Exception as exc:
            raise EncryptionError(f"Invalid encryption key: {exc}") from exc

    @staticmethod
    def generate_key() -> str:
        """Generate a new random Fernet key.

        Returns:
            A URL-safe base64-encoded 32-byte key string.
        """
        return Fernet.generate_key().decode()

    def encrypt(self, data: str | bytes) -> str:
        """Encrypt a string or bytes value.

        Args:
            data: The plaintext to encrypt.

        Returns:
            A URL-safe base64-encoded ciphertext string.
        """
        if isinstance(data, str):
            data = data.encode()
        return urlsafe_b64encode(self._fernet.encrypt(data)).decode()

    def decrypt(self, ciphertext: str | bytes) -> str:
        """Decrypt a Fernet-encrypted ciphertext.

        Args:
            ciphertext: The encrypted value to decrypt.

        Returns:
            The decrypted plaintext string.

        Raises:
            EncryptionError: If the ciphertext is invalid or was encrypted
                with a different key.
        """
        try:
            raw = urlsafe_b64decode(ciphertext)
            return self._fernet.decrypt(raw).decode()
        except InvalidToken as exc:
            raise EncryptionError("Decryption failed — invalid token or key.") from exc


def generate_secure_token(nbytes: int = 32) -> str:
    """Generate a cryptographically-secure random token.

    Args:
        nbytes: Number of random bytes to use (default: 32).

    Returns:
        A URL-safe base64-encoded token string.
    """
    return secrets.token_urlsafe(nbytes)


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks.

    Args:
        a: First string.
        b: Second string.

    Returns:
        ``True`` if the strings are equal.
    """
    return hmac.compare_digest(a.encode(), b.encode())


def sha256_hex(data: str | bytes) -> str:
    """Compute the SHA-256 digest of data and return it as a hex string.

    Args:
        data: The input to hash.

    Returns:
        Lowercase hex digest string (64 characters).
    """
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()
