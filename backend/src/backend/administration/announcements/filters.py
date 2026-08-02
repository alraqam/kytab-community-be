from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.administration.announcements.models import Announcement


class AnnouncementFilter(Filter):
    q: str | None = None
    is_published: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Announcement
        search_model_fields = ("title", "body")
        search_field_name = "q"
