from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.managers.requests import ClubJoinRequestManager
from src.backend.clubs.club_membership.schemas import ClubModerationSummary
from src.backend.clubs.clubs.models import Club
from src.backend.identity.auth.models import User
from src.backend.trust_safety.complaint.schemas import ComplaintStatus


class ClubModerationManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        from src.backend.trust_safety.complaint.managers import ComplaintManager

        self.session = session
        self.join_request_manager = ClubJoinRequestManager(session)
        self.complaint_manager = ComplaintManager(session)

    async def get_moderation_summary(
            self,
            user: User,
            club: Club,
    ) -> ClubModerationSummary:
        join_requests = await self.join_request_manager.get_club_requests(user, club)
        complaints = await self.complaint_manager.get_club_complaints(user, club)
        pending_complaints = [c for c in complaints if c.status == ComplaintStatus.pending]

        return ClubModerationSummary(
            pending_join_requests=len(join_requests),
            pending_complaints=len(pending_complaints),
            total_complaints=len(complaints),
        )
