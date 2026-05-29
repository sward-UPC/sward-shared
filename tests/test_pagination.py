from sward_shared.schemas.pagination import PaginatedResponse, PaginationParams


def test_pagination_offset():
    params = PaginationParams(page=3, page_size=10)
    assert params.offset == 20


def test_paginated_response_total_pages():
    params = PaginationParams(page=1, page_size=10)
    response = PaginatedResponse.create(items=list(range(10)), total=25, params=params)
    assert response.total_pages == 3
    assert response.page == 1


def test_paginated_response_sin_items():
    params = PaginationParams(page=1, page_size=10)
    response = PaginatedResponse.create(items=[], total=0, params=params)
    assert response.total_pages == 0
