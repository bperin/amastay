from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


@dataclass
class PaginationResult:
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Get and store pagination params in request.state
        page = request.query_params.get("page", "1")
        limit = request.query_params.get("limit", "25")

        params = Pagination.get_pagination_params(page, limit)
        request.state.pagination = params

        response = await call_next(request)
        return response


class Pagination:
    VALID_LIMITS: List[int] = [10, 25, 50, 100]
    DEFAULT_LIMIT: int = 25
    DEFAULT_PAGE: int = 1

    @staticmethod
    def get_pagination_params(page: Optional[str] = None, limit: Optional[str] = None) -> Dict[str, int]:
        try:
            page_num = max(int(page or Pagination.DEFAULT_PAGE), 1)
            limit_num = int(limit or Pagination.DEFAULT_LIMIT)
            if limit_num not in Pagination.VALID_LIMITS:
                limit_num = Pagination.DEFAULT_LIMIT
            return {"page": page_num, "limit": limit_num}
        except (ValueError, TypeError):
            return {"page": Pagination.DEFAULT_PAGE, "limit": Pagination.DEFAULT_LIMIT}
