from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Types of legal documents users may need to consent to."""

    terms_of_service = "terms_of_service"
    privacy_policy = "privacy_policy"
    community_guidelines = "community_guidelines"

class CreateLegalDocument(BaseModel):
    """Request payload for publishing a new legal document version."""

    document_type: DocumentType
    document_version: str
    is_current: bool
    content: str

class GetLegalDocument(BaseModel):
    """Response payload representing a legal document."""

    id: int
    document_type: DocumentType
    document_version: str
    is_current: bool
    content: str
    created_at: datetime
    updated_at: datetime

class CreateConsent(BaseModel):
    """Request payload for recording a user's consent to a legal document."""

    document_id: int

class GetConsent(BaseModel):
    """Response payload representing a consent record."""

    id: int
    user_id: int
    username: str | None = None
    document_id: int
    document_type: DocumentType | None = None
    document_version: str | None = None
    created_at: datetime
    updated_at: datetime