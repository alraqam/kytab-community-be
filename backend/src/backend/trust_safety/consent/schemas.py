from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    terms_of_service = "terms_of_service"
    privacy_policy = "privacy_policy"
    community_guidelines = "community_guidelines"

class CreateLegalDocument(BaseModel):
    document_type: DocumentType
    document_version: str
    is_current: bool
    content: str

class GetLegalDocument(BaseModel):
    id: int
    document_type: DocumentType
    document_version: str
    is_current: bool
    content: str
    created_at: datetime
    updated_at: datetime

class CreateConsent(BaseModel):
    document_id: int

class GetConsent(BaseModel):
    id: int
    user_id: int
    document_id: int
    created_at: datetime
    updated_at: datetime