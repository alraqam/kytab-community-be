from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.consent.filters import LegalDocumentFilter
from src.backend.trust_safety.consent.models import LegalDocument


@dataclass
class LegalDocumentRepository:
    """Data-access layer for legal document persistence and queries."""

    session: AsyncSession

    async def create_document(
            self,
            document_type: str,
            document_version: str,
            is_current: bool,
            content: str,
    ) -> LegalDocument:
        """Inserts a new legal document version.

        Args:
            document_type: Type of the legal document.
            document_version: Version identifier for this document.
            is_current: Whether this version should be marked as current.
            content: Full text content of the document.

        Returns:
            Newly created LegalDocument instance.
        """
        result = LegalDocument(
            document_type=document_type,
            document_version=document_version,
            is_current=is_current,
            content=content,
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_is_current(
            self,
            document: LegalDocument,
            status: bool,
    ) -> None:
        """Sets a document's current-version flag.

        Args:
            document: LegalDocument instance to update.
            status: New current-version flag value.
        """
        document.is_current = status
        self.session.add(document)
        await self.session.flush()

    async def get_documents(
            self,
            filters: LegalDocumentFilter
    ) -> list[LegalDocument]:
        """Lists legal documents, optionally filtered and sorted.

        Args:
            filters: LegalDocumentFilter to apply, or None for no filtering.

        Returns:
            List of matching LegalDocument instances.
        """
        stmt = select(LegalDocument)
        if filters:
            stmt = filters.filter(stmt)
            stmt = filters.sort(stmt)
        result = await self.session.execute(stmt)
        lst = result.scalars().all()
        return lst

    async def get_document_by_id(
            self,
            document_id: int
    ) -> LegalDocument | None:
        """Fetches a single legal document by ID.

        Args:
            document_id: ID of the document to fetch.

        Returns:
            Matching LegalDocument instance, or None if not found.
        """
        stmt = select(LegalDocument).where(LegalDocument.id == document_id)
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()
        return document

