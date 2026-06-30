"""Compression utilities using zstandard (zstd) for ExamVerseOS.

Example:
    >>> compressed = compress(b"hello world")
    >>> decompress(compressed)
    b'hello world'
"""

from __future__ import annotations

import zstandard


def compress(data: bytes | str, *, level: int = 3) -> bytes:
    """Compress data using zstandard (zstd).

    Args:
        data: The payload to compress.
        level: Compression level (1–22, default: 3 for speed/ratio balance).

    Returns:
        Compressed bytes.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    ctx = zstandard.ZstdCompressor(level=level)
    return ctx.compress(data)


def decompress(data: bytes) -> bytes:
    """Decompress zstd-compressed data.

    Args:
        data: Compressed bytes produced by :func:`compress`.

    Returns:
        Original uncompressed bytes.

    Raises:
        zstandard.ZstdError: If the data is not valid zstd-compressed content.
    """
    ctx = zstandard.ZstdDecompressor()
    return ctx.decompress(data)


def compress_str(text: str, *, level: int = 3) -> bytes:
    """Compress a string to zstd bytes.

    Args:
        text: The text to compress.
        level: Compression level.

    Returns:
        Compressed bytes.
    """
    return compress(text.encode("utf-8"), level=level)


def decompress_str(data: bytes) -> str:
    """Decompress zstd bytes to a string.

    Args:
        data: Compressed bytes.

    Returns:
        Decompressed UTF-8 string.
    """
    return decompress(data).decode("utf-8")


def compression_ratio(original: bytes | str, compressed: bytes) -> float:
    """Compute the compression ratio.

    Args:
        original: The uncompressed data.
        compressed: The compressed data.

    Returns:
        Ratio of original size to compressed size. Values > 1 indicate
        compression was beneficial.
    """
    if isinstance(original, str):
        original = original.encode("utf-8")
    if not compressed:
        return 1.0
    return len(original) / len(compressed)
