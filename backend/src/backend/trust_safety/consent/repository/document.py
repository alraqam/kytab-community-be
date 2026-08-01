from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.trust_safety.consent.filters import LegalDocumentFilter
from src.backend.trust_safety.consent.models import LegalDocument


@dataclass
class LegalDocumentRepository:
    session: AsyncSession

    async def create_document(
            self,
            document_type: str,
            document_version: str,
            is_current: bool,
            content: str,
    ) -> LegalDocument:
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
        document.is_current = status
        self.session.add(document)
        await self.session.flush()

    async def get_documents(
            self,
            filters: LegalDocumentFilter
    ) -> list[LegalDocument]:
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
        stmt = select(LegalDocument).where(LegalDocument.id == document_id)
        result = await self.session.execute(stmt)
        document = result.scalar_one_or_none()
        return document

