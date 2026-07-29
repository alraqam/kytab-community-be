from datetime import date

from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.clubs.reading_session.models import Milestone
from src.backend.clubs.reading_session.schemas import MilestoneBoundaryType


class MilestoneFilter(Filter):
    boundary_type: MilestoneBoundaryType | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Milestone
        search_model_fields = ("id", "text")
        ordering_model_fields = ["created_at", "target_date", "order_index"]