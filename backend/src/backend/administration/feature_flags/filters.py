from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.administration.feature_flags.models import FeatureFlag


class FeatureFlagFilter(Filter):
    """Query filter for feature flags: free-text search, enabled status, and ordering."""

    q: str | None = None
    is_enabled: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = FeatureFlag
        search_model_fields = ("key", "name")
        search_field_name = "q"
