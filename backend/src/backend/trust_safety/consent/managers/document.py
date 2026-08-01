from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.trust_safety.consent.exceptions import DocumentNotFoundError
from src.backend.trust_safety.consent.filters import LegalDocumentFilter
from src.backend.trust_safety.consent.models import LegalDocument
from src.backend.trust_safety.consent.repository.document import LegalDocumentRepository
from src.backend.trust_safety.consent.schemas import CreateLegalDocument


class LegalDocumentManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.document_repo = LegalDocumentRepository(session)


    async def create_legal_document(
            self,
            user: User,
            request: CreateLegalDocument,
    ) -> LegalDocument:
        await is_admin(user)
        result = await self.document_repo.create_document(
            document_type=request.document_type,
            document_version=request.document_version,
            is_current=request.is_current,
            content=request.content,
        )
        await self.session.commit()
        return result

    async def make_current(
            self,
            user: User,
            document: LegalDocument
    ) -> None:
        await is_admin(user)
        await self.document_repo.update_is_current(
            document=document,
            status=True
        )
        await self.session.commit()

    async def remove_current(
            self,
            user: User,
            document: LegalDocument
    ) -> None:
        await is_admin(user)
        await self.document_repo.update_is_current(
            document=document,
            status=False
        )
        await self.session.commit()

    async def get_documents(
            self,
            filters: LegalDocumentFilter
    ) -> list[LegalDocument]:
        documents = await self.document_repo.get_documents(filters)
        return documents

    async def get_document_by_id(
            self,
            document_id: int
    ) -> LegalDocument:
        result = await self.document_repo.get_document_by_id(document_id)
        if not result:
            raise DocumentNotFoundError("Document not found")
        return result