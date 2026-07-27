from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.schemas import ClubTypes, ClubPublicTypes


class ClubFilter(Filter):
    """Filter and sort parameters for admin queries on the Club model."""

    q: str | None = None
    name: str | None = None
    description: str | None = None
    club_type: ClubTypes | None = None
    is_archived: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Club
        search_model_fields = ("name", "description",)
        search_field_name = "q"


class ClubPublicFilter(Filter):
    q: str | None = None
    name: str | None = None
    description: str | None = None
    club_type: ClubPublicTypes | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Club
        search_model_fields = ("name", "description",)
        search_field_name = "q"