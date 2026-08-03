from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.trust_safety.consent.dependencies import get_legal_document_manager, get_legal_document_or_404
from src.backend.trust_safety.consent.filters import LegalDocumentFilter
from src.backend.trust_safety.consent.managers.document import LegalDocumentManager
from src.backend.trust_safety.consent.models import LegalDocument
from src.backend.trust_safety.consent.schemas import GetLegalDocument, CreateLegalDocument

router = APIRouter(
    prefix="/document",
    tags=["documents"]
)

@cbv(router)
class DocumentRouter:
    """CBV router for managing legal documents: publishing versions and toggling the current one."""

    manager: LegalDocumentManager = Depends(get_legal_document_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating documents",
        response_model=GetLegalDocument
    )
    async def create_compliant(
            self,
            request: CreateLegalDocument
    ):
        """Publishes a new legal document version."""
        result = await self.manager.create_legal_document(self.user, request)
        return result

    @router.put(
        "/{document_id}/current",
        summary="making document current",
    )
    async def make_current(
            self,
            document: LegalDocument = Depends(get_legal_document_or_404)
    ):
        """Marks a document as the current version."""
        await self.manager.make_current(self.user, document)

    @router.put(
        "/{document_id}/remove-current",
        summary="removing document current",
    )
    async def remove_current(
            self,
            document: LegalDocument = Depends(get_legal_document_or_404)
    ):
        """Unmarks a document as the current version."""
        await self.manager.remove_current(self.user, document)


    @router.get(
        "/{document_id}",
        summary="getting document by id",
        response_model=GetLegalDocument
    )
    async def get_document_by_id(
            self,
            document: LegalDocument = Depends(get_legal_document_or_404)
    ):
        """Fetches a single legal document by ID."""
        return document

    @router.get(
        "/",
        summary="getting documents",
        response_model=list[GetLegalDocument]
    )
    async def get_documents(
            self,
            filters: LegalDocumentFilter = FilterDepends(LegalDocumentFilter)
    ):
        """Lists legal documents, optionally filtered."""
        result = await self.manager.get_documents(filters)
        return result