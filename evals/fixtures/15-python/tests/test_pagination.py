import pytest
from pagination import paginate


SAMPLE_ITEMS = [{"id": i, "name": f"Item {i}"} for i in range(1, 21)]


def test_paginate_returns_correct_count():
    result = paginate(SAMPLE_ITEMS, 1, 5)
    assert len(result["items"]) == 5


def test_paginate_returns_total():
    result = paginate(SAMPLE_ITEMS, 1, 5)
    assert result["total"] == 20


def test_paginate_total_pages():
    result = paginate(SAMPLE_ITEMS, 1, 5)
    assert result["total_pages"] == 4
