from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from src.backend.trust_safety.consent.managers.consent import ConsentManager
from src.backend.trust_safety.consent.managers.document import LegalDocumentManager
from src.backend.trust_safety.consent.models import LegalDocument
from src.backend.core.dependencies import get_db


async def get_legal_document_manager(
        session: AsyncSession = Depends(get_db)
) -> LegalDocumentManager:
    return LegalDocumentManager(session)

async def get_legal_document_or_404(
        document_id: int,
        manager: LegalDocumentManager = Depends(get_legal_document_manager)
) -> LegalDocument:
    return await manager.get_document_by_id(document_id)

async def get_consent_manager(
        session: AsyncSession = Depends(get_db)
) -> ConsentManager:
    return ConsentManager(session)