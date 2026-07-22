from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.catalog.librarian.schemas import LibrarianSubmissionStatus


class LibrarianSubmissionFilter(Filter):
    q: str | None = None
    status: LibrarianSubmissionStatus | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = LibrarianSubmission
        search_model_fields = ("title", "author_name")
        search_field_name = "q"