"""Pagination utilities for ExamVerseOS list endpoints.

Example:
    >>> page = paginate(items=[1, 2, 3, 4, 5], page=1, page_size=2)
    >>> page.total
    5
    >>> page.pages
    3
"""

from __future__ import annotations

import math
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A single page of results from a paginated query.

    Attributes:
        items: The items on the current page.
        total: Total number of items across all pages.
        page: The current page number (1-indexed).
        page_size: Number of items per page.
        pages: Total number of pages.
        has_next: Whether a next page exists.
        has_prev: Whether a previous page exists.
    """

    items: list[T]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)

    model_config = {"arbitrary_types_allowed": True}

    @property
    def pages(self) -> int:
        """Total number of pages.

        Returns:
            Integer page count (minimum 1).
        """
        if self.total == 0:
            return 1
        return math.ceil(self.total / self.page_size)

    @property
    def has_next(self) -> bool:
        """True when a next page is available.

        Returns:
            Boolean indicating next page existence.
        """
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """True when a previous page is available.

        Returns:
            Boolean indicating previous page existence.
        """
        return self.page > 1

    @property
    def offset(self) -> int:
        """The SQL/query offset for the current page.

        Returns:
            Zero-based integer offset.
        """
        return (self.page - 1) * self.page_size


class PaginationParams(BaseModel):
    """Request parameters for a paginated list query.

    Attributes:
        page: Requested page number (1-indexed).
        page_size: Requested page size.
    """

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=200, description="Items per page")

    @property
    def offset(self) -> int:
        """Zero-based offset for this page.

        Returns:
            Integer offset.
        """
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Alias for ``page_size`` for SQL LIMIT clauses.

        Returns:
            Integer page size.
        """
        return self.page_size


def paginate(
    items: list[T],
    *,
    page: int,
    page_size: int,
    total: int | None = None,
) -> Page[T]:
    """Wrap a list of items in a :class:`Page` response.

    Args:
        items: The items for the current page (already sliced).
        page: Current page number (1-indexed).
        page_size: Items per page.
        total: Total item count. Defaults to ``len(items)`` when not provided.

    Returns:
        A :class:`Page` instance.
    """
    return Page(
        items=items,
        total=total if total is not None else len(items),
        page=page,
        page_size=page_size,
    )
