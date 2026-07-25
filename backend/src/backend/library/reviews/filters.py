from fastapi_filter.contrib.sqlalchemy import Filter

from backend.library.reviews.models import Review


class ReviewFilter(Filter):
    rating: int | None = None
    contains_spoiler: bool = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Review
        search_model_fields = ("id", "text")