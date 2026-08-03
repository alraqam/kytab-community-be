from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_utils.cbv import cbv

from src.backend.identity.auth.models import User
from src.backend.identity.users.dependencies import is_admin
from src.backend.trust_safety.complaint.dependencies import get_complaint_manager, get_complaint_or_404
from src.backend.trust_safety.complaint.filters import ComplaintFilter
from src.backend.trust_safety.complaint.managers import ComplaintManager
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.complaint.schemas import GetComplaint, WarnComplaintTarget

router = APIRouter(
    prefix="/admin/complaint",
    tags=["admin"]
)

@cbv(router)
class ComplaintAdminRouter:
    """CBV router for platform-level moderation of complaints: review, resolve, and enforce."""

    manager: ComplaintManager = Depends(get_complaint_manager)
    user: User = Depends(is_admin)

    @router.put(
        "/{complaint_id}/resolve",
        summary="resolving complaints",
    )
    async def resolve_complaint(
            self,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        """Marks a complaint as reviewed."""
        return await self.manager.resolve_complaint(self.user, complaint)

    @router.put(
        "/{complaint_id}/dismiss",
        summary="dismissing complaints",
    )
    async def dismiss_complaint(
            self,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        """Dismisses a complaint without action."""
        return await self.manager.dismiss_complaint(self.user, complaint)

    @router.put(
        "/{complaint_id}/remove-content",
        summary="removing reported content",
    )
    async def remove_content(
            self,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        """Deletes the content a complaint reports and resolves the complaint."""
        await self.manager.remove_complaint_content(self.user, complaint)

    @router.put(
        "/{complaint_id}/warn",
        summary="warning the reported user",
    )
    async def warn_target(
            self,
            request: WarnComplaintTarget,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        """Sends a moderation warning to a complaint's target user."""
        await self.manager.warn_complaint_target(self.user, complaint, request)

    @router.put(
        "/{complaint_id}/suspend",
        summary="suspending the reported user",
    )
    async def suspend_target(
            self,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        """Suspends a complaint's target user."""
        await self.manager.suspend_complaint_target(self.user, complaint)

    @router.put(
        "/{complaint_id}/ban",
        summary="banning the reported user",
    )
    async def ban_target(
            self,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        """Bans a complaint's target user."""
        await self.manager.ban_complaint_target(self.user, complaint)

    @router.get(
        "/",
        summary="getting complaints",
        response_model=list[GetComplaint]
    )
    async def get_complaints(
            self,
            filters: ComplaintFilter = FilterDepends(ComplaintFilter)
    ):
        """Lists complaints, optionally filtered."""
        result = await self.manager.get_complaints(filters)
        return result