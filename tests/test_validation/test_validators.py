"""Tests for domain validators."""

from __future__ import annotations

import pytest

from examverse_core.validation.validators import (
    validate_code,
    validate_email,
    validate_filename,
    validate_phone,
    validate_slug,
    validate_url,
    validate_uuid,
)


class TestEmailValidator:
    def test_valid_email(self) -> None:
        result = validate_email("user@example.com")
        assert "@" in result

    def test_invalid_email_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_email("not-an-email")

    def test_normalises_email(self) -> None:
        result = validate_email("user@EXAMPLE.COM")
        assert result == "user@example.com"


class TestSlugValidator:
    def test_valid_slug(self) -> None:
        assert validate_slug("hello-world") == "hello-world"

    def test_alphanumeric_slug(self) -> None:
        assert validate_slug("topic123") == "topic123"

    def test_slug_with_uppercase_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_slug("Hello-World")

    def test_slug_starting_with_hyphen_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_slug("-bad-slug")

    def test_empty_slug_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_slug("")

    def test_too_long_slug_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_slug("a" * 101, max_length=100)


class TestUUIDValidator:
    def test_valid_uuid(self) -> None:
        uid = "550e8400-e29b-41d4-a716-446655440000"
        assert validate_uuid(uid) == uid

    def test_invalid_uuid_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_uuid("not-a-uuid")


class TestCodeValidator:
    def test_valid_code(self) -> None:
        assert validate_code("PHY_101") == "PHY_101"

    def test_lowercase_code_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_code("physics")

    def test_starting_with_digit_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_code("1PHY")


class TestURLValidator:
    def test_valid_http_url(self) -> None:
        assert validate_url("http://example.com") == "http://example.com"

    def test_valid_https_url(self) -> None:
        assert validate_url("https://example.com/path?q=1")

    def test_invalid_url_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_url("ftp://example.com")

    def test_plain_string_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_url("not-a-url")


class TestFilenameValidator:
    def test_valid_filename(self) -> None:
        assert validate_filename("document.pdf") == "document.pdf"

    def test_dangerous_extension_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_filename("malware.exe")

    def test_empty_filename_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_filename("")

    def test_special_chars_raise(self) -> None:
        with pytest.raises(ValueError):
            validate_filename("file/../etc/passwd")


class TestPhoneValidator:
    def test_valid_e164(self) -> None:
        assert validate_phone("+919876543210") == "+919876543210"

    def test_missing_plus_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_phone("919876543210")

    def test_too_short_raises(self) -> None:
        with pytest.raises(ValueError):
            validate_phone("+1234")
