from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.trust_safety.consent.exceptions import DocumentNotFoundError
from src.backend.trust_safety.consent.filters import LegalDocumentFilter
from src.backend.trust_safety.consent.models import LegalDocument
from src.backend.trust_safety.consent.repository.document import LegalDocumentRepository
from src.backend.trust_safety.consent.schemas import CreateLegalDocument


class LegalDocumentManager:
    """Handles legal document business logic: publishing versions and toggling which one is current."""

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
        """Publishes a new legal document version.

        Args:
            user: User performing the action; must be an admin.
            request: CreateLegalDocument payload with the document type, version, and content.

        Returns:
            Newly created LegalDocument instance.

        Raises:
            PermissionDeniedError: When the user is not an admin.
        """
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
        """Marks a document as the current version.

        Args:
            user: User performing the action; must be an admin.
            document: LegalDocument instance to mark as current.

        Raises:
            PermissionDeniedError: When the user is not an admin.
        """
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
        """Unmarks a document as the current version.

        Args:
            user: User performing the action; must be an admin.
            document: LegalDocument instance to unmark.

        Raises:
            PermissionDeniedError: When the user is not an admin.
        """
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
        """Lists legal documents matching the given filters.

        Args:
            filters: LegalDocumentFilter with search, type, and status criteria.

        Returns:
            List of matching LegalDocument instances.
        """
        documents = await self.document_repo.get_documents(filters)
        return documents

    async def get_document_by_id(
            self,
            document_id: int
    ) -> LegalDocument:
        """Fetches a single legal document by ID.

        Args:
            document_id: ID of the document to fetch.

        Returns:
            Matching LegalDocument instance.

        Raises:
            DocumentNotFoundError: When no document matches the ID.
        """
        result = await self.document_repo.get_document_by_id(document_id)
        if not result:
            raise DocumentNotFoundError("Document not found")
        return result