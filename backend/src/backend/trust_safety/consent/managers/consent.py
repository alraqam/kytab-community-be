from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.trust_safety.consent.exceptions import DocumentAlreadyConsentedError, OutdatedDocumentError, \
    ConsentNotFoundError
from src.backend.trust_safety.consent.managers.document import LegalDocumentManager
from src.backend.trust_safety.consent.models import LegalDocument, ConsentRecords

from src.backend.trust_safety.consent.repository.consent import ConsentRepository
from src.backend.trust_safety.consent.schemas import CreateConsent


class ConsentManager:
    """Handles consent business logic: recording and retrieving a user's consent to legal documents."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.consent_repo = ConsentRepository(session)
        self.document_manager = LegalDocumentManager(session)

    async def create_consent(
            self,
            user: User,
            request: CreateConsent
    ) -> ConsentRecords:
        """Records a user's consent to a legal document, provided it's the current version.

        Args:
            user: User giving consent.
            request: CreateConsent payload with the document ID.

        Returns:
            Newly created ConsentRecords instance.

        Raises:
            DocumentNotFoundError: When no document matches request.document_id.
            OutdatedDocumentError: When the document is not the current version.
            DocumentAlreadyConsentedError: When the user has already consented to this document.
        """
        document = await self.document_manager.get_document_by_id(request.document_id)
        if not document.is_current:
            raise OutdatedDocumentError("Document is outdated")
        try:
            result = await self.consent_repo.create_consent(
                user_id=user.id,
                document_id=document.id
            )
            await self.session.commit()
            return result
        except IntegrityError as e:
            raise DocumentAlreadyConsentedError("Document already consented")

    async def get_user_consents(
            self,
            user: User
    ) -> list[ConsentRecords]:
        """Lists all consent records belonging to a user.

        Args:
            user: User whose consents to list.

        Returns:
            List of ConsentRecords instances.
        """
        consents = await self.consent_repo.get_user_consents(user.id)
        return consents

    async def get_consent_by_id(
            self,
            consent_id: int
    ) -> ConsentRecords:
        """Fetches a single consent record by ID.

        Args:
            consent_id: ID of the consent record to fetch.

        Returns:
            Matching ConsentRecords instance.

        Raises:
            ConsentNotFoundError: When no consent record matches the ID.
        """
        result = await self.consent_repo.get_consent_by_id(consent_id)
        if not result:
            raise ConsentNotFoundError("Consent not found")
        return result