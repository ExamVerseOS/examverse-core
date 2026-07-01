"""Version information helper for the CLI."""

from __future__ import annotations

import sys

import examverse_core


def version_string() -> str:
    """Return a formatted version string."""
    return (
        f"examverse-core {examverse_core.__version__} "
        f"(Python {sys.version.split()[0]})"
    )
