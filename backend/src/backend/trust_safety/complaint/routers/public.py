from fastapi import APIRouter, Depends, status
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.dependencies.auth import get_current_user
from src.backend.identity.auth.models.auth import User
from src.backend.trust_safety.complaint.dependencies.complaint import get_complaint_manager
from src.backend.trust_safety.complaint.managers.complaint import ComplaintManager
from src.backend.trust_safety.complaint.schemas.complaint import GetComplaint, CreateComplaint
from src.backend.core.responses import error_responses

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
        response_model=GetComplaint,
        status_code=status.HTTP_201_CREATED,
        responses=error_responses(401, 404),
    )
    async def create_compliant(
            self,
            request: CreateComplaint
    ):
        """Files a new complaint."""
        result = await self.manager.create_compliant(self.user, request)
        return result