from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.identity.auth.models import User
from src.backend.identity.auth.schemas import UserRoleEnum


class UserFilter(Filter):
    """Filter and sort parameters for querying the User model."""

    q: str | None = None
    fullname: str | None = None
    role: UserRoleEnum | None = None
    username: str | None = None
    is_active: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = User
        search_model_fields = ("id", )
        search_field_name = "q"