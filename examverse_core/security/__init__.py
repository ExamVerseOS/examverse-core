"""ExamVerse security utilities — JWT, permissions, audit, and crypto."""

from examverse_core.security.audit import AuditEntry, AuditWriter
from examverse_core.security.crypto import (
    PasswordHasher,
    SymmetricEncryption,
    constant_time_compare,
    generate_secure_token,
    sha256_hex,
)
from examverse_core.security.exceptions import (
    EncryptionError,
    PermissionDeniedError,
    SecurityError,
    TokenDecodeError,
    TokenExpiredError,
)
from examverse_core.security.jwt import JWTHelper
from examverse_core.security.permissions import (
    Permission,
    PermissionChecker,
    RoleDefinition,
)

__all__ = [
    "JWTHelper",
    "Permission",
    "PermissionChecker",
    "RoleDefinition",
    "AuditEntry",
    "AuditWriter",
    "PasswordHasher",
    "SymmetricEncryption",
    "generate_secure_token",
    "constant_time_compare",
    "sha256_hex",
    "SecurityError",
    "TokenExpiredError",
    "TokenDecodeError",
    "PermissionDeniedError",
    "EncryptionError",
]
