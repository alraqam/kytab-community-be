from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.trust_safety.consent.managers.consent import ConsentManager
from src.backend.trust_safety.consent.managers.document import LegalDocumentManager
from src.backend.trust_safety.consent.models import LegalDocument
from src.backend.core.dependencies import get_db


async def get_legal_document_manager(
        session: AsyncSession = Depends(get_db)
) -> LegalDocumentManager:
    """Builds a LegalDocumentManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        LegalDocumentManager instance.
    """
    return LegalDocumentManager(session)

async def get_legal_document_or_404(
        document_id: int,
        manager: LegalDocumentManager = Depends(get_legal_document_manager)
) -> LegalDocument:
    """Resolves a legal document by path parameter or raises if it doesn't exist.

    Args:
        document_id: ID of the document from the path.
        manager: LegalDocumentManager used to look up the document.

    Returns:
        LegalDocument instance.

    Raises:
        DocumentNotFoundError: When no document matches the ID.
    """
    return await manager.get_document_by_id(document_id)

async def get_consent_manager(
        session: AsyncSession = Depends(get_db)
) -> ConsentManager:
    """Builds a ConsentManager bound to the request-scoped database session.

    Args:
        session: Database session injected by get_db.

    Returns:
        ConsentManager instance.
    """
    return ConsentManager(session)