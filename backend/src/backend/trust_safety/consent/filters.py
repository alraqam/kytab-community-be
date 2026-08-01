from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.trust_safety.consent.models import LegalDocument
from src.backend.trust_safety.consent.schemas import DocumentType


class LegalDocumentFilter(Filter):

    q: str | None = None
    document_type: DocumentType | None = None
    is_current: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = LegalDocument
        search_model_fields = ("id", "content", "document_version")
        search_field_name = "q"