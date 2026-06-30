"""Tests for pagination utilities."""

from __future__ import annotations

import pytest

from examverse_core.utils.pagination import Page, PaginationParams, paginate


class TestPaginate:
    def test_basic_pagination(self) -> None:
        page = paginate([1, 2, 3], page=1, page_size=3, total=10)
        assert page.total == 10
        assert page.page == 1
        assert page.pages == 4
        assert page.has_next
        assert not page.has_prev

    def test_last_page(self) -> None:
        page = paginate([10], page=4, page_size=3, total=10)
        assert not page.has_next
        assert page.has_prev

    def test_empty_results(self) -> None:
        page = paginate([], page=1, page_size=10, total=0)
        assert page.pages == 1

    def test_offset(self) -> None:
        page = paginate([], page=3, page_size=10, total=50)
        assert page.offset == 20


class TestPaginationParams:
    def test_defaults(self) -> None:
        params = PaginationParams()
        assert params.page == 1
        assert params.page_size == 20

    def test_offset_calculation(self) -> None:
        params = PaginationParams(page=3, page_size=10)
        assert params.offset == 20
        assert params.limit == 10

    def test_max_page_size(self) -> None:
        with pytest.raises(Exception):
            PaginationParams(page_size=201)
