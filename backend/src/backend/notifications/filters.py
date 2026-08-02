from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.notifications.models import Notification
from src.backend.notifications.schemas import NotificationCategory


class NotificationFilter(Filter):
    q: str | None = None
    category: NotificationCategory | None = None
    club_id: int | None = None
    is_read: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Notification
        search_model_fields = ("id", "title", "body")
        search_field_name = "q"
