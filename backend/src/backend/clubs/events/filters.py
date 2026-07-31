from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.clubs.events.models import EventRSVP
from src.backend.clubs.events.schemas import RSVPStatus


class EventRSVPFilter(Filter):
    response: RSVPStatus | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = EventRSVP
        search_model_fields = ("id",)
