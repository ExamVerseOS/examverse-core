"""Tests for security crypto utilities."""

from __future__ import annotations

import pytest

from examverse_core.security.crypto import (
    PasswordHasher,
    SymmetricEncryption,
    constant_time_compare,
    generate_secure_token,
    sha256_hex,
)
from examverse_core.security.exceptions import EncryptionError


class TestPasswordHasher:
    def test_hash_and_verify(self) -> None:
        h = PasswordHasher()
        hashed = h.hash("my-password")
        assert h.verify("my-password", hashed)

    def test_wrong_password_returns_false(self) -> None:
        h = PasswordHasher()
        hashed = h.hash("correct")
        assert not h.verify("wrong", hashed)

    def test_needs_rehash_false_for_fresh_hash(self) -> None:
        h = PasswordHasher()
        hashed = h.hash("pass")
        assert not h.needs_rehash(hashed)


class TestSymmetricEncryption:
    def test_encrypt_and_decrypt(self) -> None:
        key = SymmetricEncryption.generate_key()
        enc = SymmetricEncryption(key)
        ciphertext = enc.encrypt("hello world")
        assert enc.decrypt(ciphertext) == "hello world"

    def test_wrong_key_raises(self) -> None:
        key1 = SymmetricEncryption.generate_key()
        key2 = SymmetricEncryption.generate_key()
        enc1 = SymmetricEncryption(key1)
        enc2 = SymmetricEncryption(key2)
        ciphertext = enc1.encrypt("secret")
        with pytest.raises(EncryptionError):
            enc2.decrypt(ciphertext)

    def test_invalid_key_raises(self) -> None:
        with pytest.raises(EncryptionError):
            SymmetricEncryption("not-a-valid-fernet-key")


class TestHelpers:
    def test_generate_secure_token(self) -> None:
        token = generate_secure_token()
        assert len(token) > 20

    def test_constant_time_compare_equal(self) -> None:
        assert constant_time_compare("abc", "abc")

    def test_constant_time_compare_unequal(self) -> None:
        assert not constant_time_compare("abc", "xyz")

    def test_sha256_hex(self) -> None:
        digest = sha256_hex("hello")
        assert len(digest) == 64
        assert digest == sha256_hex(b"hello")
