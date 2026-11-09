from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.trust_safety.consent.dependencies.consent import get_consent_manager
from src.backend.trust_safety.consent.managers.consent import ConsentManager
from src.backend.trust_safety.consent.schemas.consent import GetConsent, CreateConsent
from src.backend.core.responses import error_responses

router = APIRouter(
    prefix="/consent",
    tags=["consent"]
)

@cbv(router)
class ConsentRouter:
    """CBV router for recording and viewing the current user's consent to legal documents."""

    manager: ConsentManager = Depends(get_consent_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/create-consent",
        summary="creating consents",
        response_model=GetConsent,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 404, 409),
    )
    async def create_consent(
            self,
            request: CreateConsent
    ):
        """Records the current user's consent to a legal document."""
        result = await self.manager.create_consent(self.user, request)
        return result

    @router.get(
        "/",
        summary="getting current user consents",
        response_model=list[GetConsent],
        status_code=status.HTTP_200_OK,
        responses=error_responses(401),
    )
    async def get_user_consents(
            self,
    ):
        """Lists the current user's consent records."""
        result = await self.manager.get_user_consents(self.user)
        return result

    @router.get(
        "/{consent_id}",
        summary="getting consent by id",
        response_model=GetConsent,
        status_code=status.HTTP_200_OK,
        responses=error_responses(401, 404),
    )
    async def get_consent_by_id(
            self,
            consent_id: int
    ):
        """Fetches a single consent record by ID."""
        result = await self.manager.get_consent_by_id(consent_id)
        return result