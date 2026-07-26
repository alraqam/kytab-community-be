from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.library.reviews.models import Review


class ReviewFilter(Filter):
    rating: float | None = None
    contains_spoiler: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Review
        search_model_fields = ("id", "text")