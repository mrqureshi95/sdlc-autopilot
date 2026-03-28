"""
Pagination utility for list data.

BUG: Off-by-one error in the slice calculation. Page 1 should return
items 0-9 (for per_page=10), but the current formula starts at index 1
instead of 0, skipping the first item on every page.
"""


def paginate(items, page, per_page):
    # BUG: start should be (page - 1) * per_page, not page * per_page
    start = page * per_page
    end = start + per_page
    page_items = items[start:end]

    return {
        "items": page_items,
        "page": page,
        "per_page": per_page,
        "total": len(items),
        "total_pages": -(-len(items) // per_page),  # ceiling division
    }


def get_page_range(total_pages, current_page, window=2):
    """Return a range of page numbers to display in pagination controls."""
    # Same off-by-one pattern: should be max(1, ...) not max(0, ...)
    start = max(0, current_page - window)
    end = min(total_pages, current_page + window)
    return list(range(start, end + 1))
