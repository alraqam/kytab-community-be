from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.trust_safety.consent.dependencies import get_consent_manager
from src.backend.trust_safety.consent.managers.consent import ConsentManager
from src.backend.trust_safety.consent.schemas import GetConsent, CreateConsent

router = APIRouter(
    prefix="/consent",
    tags=["consent"]
)

@cbv(router)
class ConsentRouter:
    manager: ConsentManager = Depends(get_consent_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/create consent",
        summary="creating consents",
        response_model=GetConsent,
    )
    async def create_consent(
            self,
            request: CreateConsent
    ):
        result = await self.manager.create_consent(self.user, request)
        return result

    @router.get(
        "/",
        summary="getting current user consents",
        response_model=list[GetConsent]
    )
    async def get_user_consents(
            self,
    ):
        result = await self.manager.get_user_consents(self.user)
        return result

    @router.get(
        "/{consent_id}",
        summary="getting consent by id",
        response_model=GetConsent
    )
    async def get_consent_by_id(
            self,
            consent_id: int
    ):
        result = await self.manager.get_consent_by_id(consent_id)
        return result