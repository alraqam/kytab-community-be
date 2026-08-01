from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.complaint.schemas import ComplaintObjectType, ComplaintCategory, ComplaintStatus


class ComplaintFilter(Filter):

    q: str | None = None
    object_type: ComplaintObjectType | None = None
    category: ComplaintCategory | None = None
    status: ComplaintStatus | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = Complaint
        search_model_fields = ("id",)
        search_field_name = "q"