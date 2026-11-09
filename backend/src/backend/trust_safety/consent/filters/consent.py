from fastapi_filter.contrib.sqlalchemy import Filter

from src.backend.trust_safety.consent.models.consent import LegalDocument
from src.backend.trust_safety.consent.schemas.consent import DocumentType


class LegalDocumentFilter(Filter):
    """Query filter for legal documents: free-text search, document type, current status, and ordering."""

    q: str | None = None
    document_type: DocumentType | None = None
    is_current: bool | None = None
    order_by: list[str] | None = None

    class Constants(Filter.Constants):
        model = LegalDocument
        search_model_fields = ("id", "content", "document_version")
        search_field_name = "q"