from sqlalchemy import Column, BigInteger, ForeignKey, String, Boolean, DateTime, Text, UniqueConstraint

from src.backend.core.models import Base, IntIdMixin, TimeActionMixin


class LegalDocument(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "legal_documents"

    document_type = Column(String(100), nullable=False)
    document_version = Column(String(100), nullable=False)
    is_current = Column(Boolean, nullable=False)
    content = Column(Text, nullable=False)


class ConsentRecords(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "consent_records"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    document_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "document_id", name="uq_user_document"),
    )
