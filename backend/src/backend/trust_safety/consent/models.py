from sqlalchemy import Column, BigInteger, ForeignKey, String, Boolean, DateTime, Text, UniqueConstraint, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin
from src.backend.identity.auth.models import User


class LegalDocument(Base, IntIdMixin, TimeActionMixin):
    """ORM model representing a versioned legal document (e.g. terms of service, privacy policy)."""

    __tablename__ = "legal_documents"

    document_type = Column(String(100), nullable=False)
    document_version = Column(String(100), nullable=False)
    is_current = Column(Boolean, nullable=False)
    content = Column(Text, nullable=False)


class ConsentRecords(Base, IntIdMixin, TimeActionMixin):
    """ORM model recording that a user has consented to a specific legal document."""

    __tablename__ = "consent_records"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    document_id = Column(BigInteger, ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "document_id", name="uq_user_document"),
    )

ConsentRecords.username = column_property(
    select(User.username)
    .where(User.id == ConsentRecords.user_id)
    .correlate_except(User)
    .scalar_subquery()
)
ConsentRecords.document_type = column_property(
    select(LegalDocument.document_type)
    .where(LegalDocument.id == ConsentRecords.document_id)
    .correlate_except(LegalDocument)
    .scalar_subquery()
)
ConsentRecords.document_version = column_property(
    select(LegalDocument.document_version)
    .where(LegalDocument.id == ConsentRecords.document_id)
    .correlate_except(LegalDocument)
    .scalar_subquery()
)
