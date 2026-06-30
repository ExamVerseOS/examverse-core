"""JWT helper utilities for the ExamVerseOS ecosystem.

Provides stateless token creation and validation. No authentication flow
is implemented here — this module supplies reusable building blocks for
downstream services (examverse-api, examverse-admin, etc.).

Example:
    >>> helper = JWTHelper(secret="s3cr3t", algorithm="HS256")
    >>> token = helper.create_access_token({"sub": "user-id", "role": "student"})
    >>> payload = helper.decode(token)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from examverse_core.security.exceptions import TokenDecodeError, TokenExpiredError


class JWTHelper:
    """Stateless JWT creation and validation helper.

    Attributes:
        _secret: The HMAC signing secret.
        _algorithm: The JWT algorithm (default HS256).
        _access_expire_minutes: Access token lifetime in minutes.
        _refresh_expire_days: Refresh token lifetime in days.
    """

    def __init__(
        self,
        secret: str,
        algorithm: str = "HS256",
        access_expire_minutes: int = 30,
        refresh_expire_days: int = 7,
    ) -> None:
        """Initialise the helper with signing credentials.

        Args:
            secret: The HMAC secret key. Must be at least 32 characters in
                production environments.
            algorithm: JWT signing algorithm.
            access_expire_minutes: Lifetime of access tokens in minutes.
            refresh_expire_days: Lifetime of refresh tokens in days.
        """
        self._secret = secret
        self._algorithm = algorithm
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_days = refresh_expire_days

    def create_access_token(
        self,
        payload: dict[str, Any],
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT access token.

        Args:
            payload: Claims to embed in the token.
            expires_delta: Custom expiry override. Defaults to the configured
                ``access_expire_minutes``.

        Returns:
            A signed JWT string.
        """
        delta = expires_delta or timedelta(minutes=self._access_expire_minutes)
        return self._encode(payload, delta, token_type="access")

    def create_refresh_token(
        self,
        payload: dict[str, Any],
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT refresh token.

        Args:
            payload: Claims to embed in the token.
            expires_delta: Custom expiry override. Defaults to the configured
                ``refresh_expire_days``.

        Returns:
            A signed JWT string.
        """
        delta = expires_delta or timedelta(days=self._refresh_expire_days)
        return self._encode(payload, delta, token_type="refresh")

    def _encode(
        self,
        payload: dict[str, Any],
        expires_delta: timedelta,
        token_type: str,
    ) -> str:
        """Sign and encode a JWT with standard claims.

        Args:
            payload: Caller-supplied claims.
            expires_delta: Token lifetime.
            token_type: The ``token_type`` claim value.

        Returns:
            Signed JWT string.
        """
        now = datetime.now(tz=timezone.utc)
        data = {
            **payload,
            "iat": now,
            "exp": now + expires_delta,
            "token_type": token_type,
        }
        return jwt.encode(data, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT, returning its claims.

        Args:
            token: The JWT string to decode.

        Returns:
            The decoded payload dictionary.

        Raises:
            TokenExpiredError: If the token has passed its ``exp`` claim.
            TokenDecodeError: If the token is malformed, tampered, or
                uses an unexpected algorithm.
        """
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except ExpiredSignatureError as exc:
            raise TokenExpiredError() from exc
        except JWTError as exc:
            raise TokenDecodeError(str(exc)) from exc

    def decode_unverified(self, token: str) -> dict[str, Any]:
        """Decode a JWT without signature verification.

        **Warning:** Use only for diagnostics or token inspection, never for
        authentication decisions.

        Args:
            token: The JWT string to decode.

        Returns:
            The raw (unverified) payload dictionary.
        """
        return jwt.get_unverified_claims(token)
