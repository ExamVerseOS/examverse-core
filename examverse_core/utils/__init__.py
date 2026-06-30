"""ExamVerse general-purpose utility modules."""

from examverse_core.utils.compression import compress, decompress
from examverse_core.utils.dates import format_iso, human_readable_duration, parse_iso, utcnow
from examverse_core.utils.hashing import hmac_sha256_hex, md5_hex, sha256_hex, sha512_hex
from examverse_core.utils.identifiers import (
    content_hash,
    generate_correlation_id,
    generate_id,
    generate_namespaced_id,
    generate_short_id,
)
from examverse_core.utils.pagination import Page, PaginationParams, paginate
from examverse_core.utils.reflection import get_subclasses, import_class, is_async_callable
from examverse_core.utils.retry import retry, retry_call
from examverse_core.utils.serialization import from_json, model_to_dict, model_to_json, to_json

__all__ = [
    "paginate",
    "Page",
    "PaginationParams",
    "retry",
    "retry_call",
    "utcnow",
    "format_iso",
    "parse_iso",
    "human_readable_duration",
    "sha256_hex",
    "sha512_hex",
    "md5_hex",
    "hmac_sha256_hex",
    "compress",
    "decompress",
    "import_class",
    "get_subclasses",
    "is_async_callable",
    "generate_id",
    "generate_short_id",
    "generate_namespaced_id",
    "generate_correlation_id",
    "content_hash",
    "to_json",
    "from_json",
    "model_to_dict",
    "model_to_json",
]
