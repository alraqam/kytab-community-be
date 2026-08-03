from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.clubs.club_membership.models import ClubMembership
from src.backend.clubs.club_membership.schemas import MemberRole


class ClubMembersFilter(Filter):
    """Query filter for club memberships: role and ordering."""

    role: MemberRole | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = ClubMembership
        search_model_fields = ("id",)