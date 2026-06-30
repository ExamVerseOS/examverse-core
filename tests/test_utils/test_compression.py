"""Tests for zstd compression utilities."""

from __future__ import annotations

from examverse_core.utils.compression import (
    compress,
    compress_str,
    compression_ratio,
    decompress,
    decompress_str,
)


class TestCompression:
    def test_round_trip_bytes(self) -> None:
        original = b"hello world " * 100
        compressed = compress(original)
        assert decompress(compressed) == original

    def test_round_trip_string(self) -> None:
        original = "ExamVerse Core " * 50
        compressed = compress(original)
        assert decompress(compressed).decode() == original

    def test_compress_str_round_trip(self) -> None:
        text = "hello examverse"
        assert decompress_str(compress_str(text)) == text

    def test_compression_ratio_positive(self) -> None:
        data = b"aaaa" * 1000
        compressed = compress(data)
        ratio = compression_ratio(data, compressed)
        assert ratio > 1.0

    def test_compression_ratio_empty(self) -> None:
        ratio = compression_ratio(b"data", b"")
        assert ratio == 1.0
