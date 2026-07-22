from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.catalog.books.models import Author, Edition, Genre, Series, Work


class WorkFilter(Filter):
    """Filter and sort parameters for querying the Work model."""

    q: str | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Work
        search_model_fields = ("canonical_title", "description")
        search_field_name = "q"

class EditionFilter(Filter):
    """Filter and sort parameters for querying the Edition model."""

    work_id: int | None = None
    language: str | None = None
    q: str | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Edition
        search_model_fields = ("title", "isbn")
        search_field_name = "q"

class AuthorFilter(Filter):
    """Filter and sort parameters for querying the Author model."""

    q: str | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Author
        search_model_fields = ("name",)
        search_field_name = "q"

class SeriesFilter(Filter):
    """Filter and sort parameters for querying the Series model."""

    q: str | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Series
        search_model_fields = ("name",)
        search_field_name = "q"

class GenreFilter(Filter):
    """Filter and sort parameters for querying the Genre model."""

    q: str | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Genre
        search_model_fields = ("name", "slug")
        search_field_name = "q"
