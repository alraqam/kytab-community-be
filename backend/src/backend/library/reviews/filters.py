from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.library.reviews.models import Review


class ReviewFilter(Filter):
    """Query filter for reviews: rating, spoiler flag, free-text search, and ordering."""

    rating: float | None = None
    rating__gte: float | None = None
    contains_spoiler: bool | None = None
    order_by: list[str] | None = None
    search: str | None = None

    class Constants(Filter.Constants):
        model = Review
        search_model_fields = ("id", "text")
        ordering_model_fields = ["created_at", "likes_count", "rating"]