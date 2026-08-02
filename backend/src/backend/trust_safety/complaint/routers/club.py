from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv

from src.backend.clubs.clubs.dependencies import get_club_or_404
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.dependencies import get_current_user
from src.backend.identity.auth.models import User
from src.backend.trust_safety.complaint.dependencies import get_complaint_manager, get_complaint_or_404
from src.backend.trust_safety.complaint.managers import ComplaintManager
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.complaint.schemas import GetComplaint

router = APIRouter(
    prefix="/{club_id}/complaint",
    tags=["complaints"]
)

@cbv(router)
class ComplaintClubRouter:
    manager: ComplaintManager = Depends(get_complaint_manager)
    user: User = Depends(get_current_user)
    club: Club = Depends(get_club_or_404)

    @router.get(
        "/",
        summary="getting club complaints",
        response_model=list[GetComplaint]
    )
    async def get_club_complaints(self):
        result = await self.manager.get_club_complaints(self.user, self.club)
        return result

    @router.put(
        "/{complaint_id}/escalate",
        summary="escalating complaint to platform moderation",
    )
    async def escalate_complaint(
            self,
            complaint: Complaint = Depends(get_complaint_or_404)
    ):
        await self.manager.escalate_complaint(self.user, self.club, complaint)
