"""Serialization helpers using orjson for high-performance JSON encoding.

Example:
    >>> from examverse_core.utils.serialization import to_json, from_json
    >>> blob = to_json({"key": "value"})
    >>> data = from_json(blob)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

import orjson


def _default_serializer(obj: Any) -> Any:
    """Custom serializer for types not handled by orjson natively.

    Args:
        obj: The object to serialise.

    Returns:
        A JSON-serialisable representation.

    Raises:
        TypeError: If the type is not supported.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, set | frozenset):
        return sorted(str(x) for x in obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def to_json(data: Any, *, indent: bool = False) -> bytes:
    """Serialise data to a JSON byte string using orjson.

    Args:
        data: Any JSON-serialisable object.
        indent: When ``True``, pretty-print with two-space indentation.

    Returns:
        A UTF-8 encoded JSON byte string.
    """
    options = orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_UUID
    if indent:
        options |= orjson.OPT_INDENT_2
    return orjson.dumps(data, default=_default_serializer, option=options)


def to_json_str(data: Any, *, indent: bool = False) -> str:
    """Serialise data to a JSON string.

    Args:
        data: Any JSON-serialisable object.
        indent: When ``True``, pretty-print.

    Returns:
        A UTF-8 JSON string.
    """
    return to_json(data, indent=indent).decode("utf-8")


def from_json(raw: bytes | str) -> Any:
    """Deserialise a JSON byte string or string.

    Args:
        raw: The JSON payload to parse.

    Returns:
        The parsed Python object.
    """
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return orjson.loads(raw)


def model_to_dict(model: Any, *, exclude_none: bool = False) -> dict[str, Any]:
    """Convert a Pydantic model instance to a plain dictionary.

    Args:
        model: A Pydantic ``BaseModel`` instance.
        exclude_none: When ``True``, omit fields whose value is ``None``.

    Returns:
        Dictionary representation of the model.
    """
    return model.model_dump(exclude_none=exclude_none)


def model_to_json(model: Any, *, exclude_none: bool = False, indent: bool = False) -> str:
    """Serialise a Pydantic model to a JSON string via orjson.

    Args:
        model: A Pydantic ``BaseModel`` instance.
        exclude_none: When ``True``, omit ``None`` fields.
        indent: When ``True``, pretty-print.

    Returns:
        A UTF-8 JSON string.
    """
    return to_json_str(model_to_dict(model, exclude_none=exclude_none), indent=indent)
