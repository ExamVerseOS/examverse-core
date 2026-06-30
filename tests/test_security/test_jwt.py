"""Tests for JWTHelper — token creation and validation."""

from __future__ import annotations

from datetime import timedelta

import pytest

from examverse_core.security.exceptions import TokenDecodeError, TokenExpiredError
from examverse_core.security.jwt import JWTHelper


@pytest.fixture
def helper() -> JWTHelper:
    return JWTHelper(secret="a" * 32, algorithm="HS256")


class TestAccessTokens:
    def test_create_and_decode(self, helper: JWTHelper) -> None:
        token = helper.create_access_token({"sub": "user-1"})
        payload = helper.decode(token)
        assert payload["sub"] == "user-1"
        assert payload["token_type"] == "access"

    def test_expired_token_raises(self, helper: JWTHelper) -> None:
        token = helper.create_access_token(
            {"sub": "user-1"}, expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(TokenExpiredError):
            helper.decode(token)

    def test_tampered_token_raises(self, helper: JWTHelper) -> None:
        token = helper.create_access_token({"sub": "user-1"})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(TokenDecodeError):
            helper.decode(tampered)


class TestRefreshTokens:
    def test_refresh_token_type(self, helper: JWTHelper) -> None:
        token = helper.create_refresh_token({"sub": "user-1"})
        payload = helper.decode(token)
        assert payload["token_type"] == "refresh"


class TestDecodeUnverified:
    def test_reads_payload_without_verification(self, helper: JWTHelper) -> None:
        token = helper.create_access_token({"sub": "user-1"})
        payload = helper.decode_unverified(token)
        assert payload["sub"] == "user-1"
