from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.trust_safety.complaint.dependencies import get_complaint_manager
from src.backend.trust_safety.complaint.managers import ComplaintManager
from src.backend.trust_safety.complaint.schemas import GetComplaint, CreateComplaint

router = APIRouter(
    prefix="/complaint",
    tags=["complaints"]
)

@cbv(router)
class ComplaintPublicRouter:
    """CBV router for filing complaints against content or users."""

    manager: ComplaintManager = Depends(get_complaint_manager)
    user: User = Depends(get_current_user)

    @router.post(
        "/",
        summary="creating complaints",
        response_model=GetComplaint
    )
    async def create_compliant(
            self,
            request: CreateComplaint
    ):
        """Files a new complaint."""
        result = await self.manager.create_compliant(self.user, request)
        return result