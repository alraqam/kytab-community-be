from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.managers import ClubManager
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.library.reviews.managers.comments import ReviewCommentManager
from src.backend.library.reviews.managers.review import ReviewManager
from src.backend.trust_safety.complaint.exceptions import ComplaintStatusError, ComplaintNotFoundError
from src.backend.trust_safety.complaint.filters import ComplaintFilter
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.complaint.repository import ComplaintRepository
from src.backend.trust_safety.complaint.schemas import CreateComplaint, ComplaintObjectType, ComplaintStatus


class ComplaintManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.complaint_repo = ComplaintRepository(session)
        self.review_manager = ReviewManager(session)
        self.club_manager = ClubManager(session)
        self.comment_manager = ReviewCommentManager(session)
        self.user_manager = UserManager(session)


    async def create_compliant(
            self,
            user: User,
            request: CreateComplaint,
    ) -> Complaint:
        match request.object_type:
            case ComplaintObjectType.review:
                await self.review_manager.get_review_by_id(request.object_id)
            case ComplaintObjectType.comment:
                await self.comment_manager.get_comment_by_id(request.object_id)
            case ComplaintObjectType.club:
                await self.club_manager.get_club_by_id(request.object_id)
            case ComplaintObjectType.user:
                await self.user_manager.get_user_by_id(request.object_id)

        result = await self.complaint_repo.create_complaint(
            reporter_id=user.id,
            object_type=request.object_type,
            object_id=request.object_id,
            category=request.category,
            comment=request.comment,
        )
        await self.session.commit()
        return result

    async def resolve_complaint(
            self,
            user: User,
            complaint: Complaint
    ) -> None:
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")
        await self.complaint_repo.resolve_complaint(
            user_id=user.id,
            complaint=complaint
        )
        await self.complaint_repo.update_complaint_status(complaint, ComplaintStatus.reviewed)
        await self.session.commit()

    async def dismiss_complaint(
            self,
            user: User,
            complaint: Complaint
    ) -> None:
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")
        await self.complaint_repo.resolve_complaint(
            user_id=user.id,
            complaint=complaint
        )
        await self.complaint_repo.update_complaint_status(complaint, ComplaintStatus.dismissed)
        await self.session.commit()

    async def get_complaints(
            self,
            filters: ComplaintFilter
    ) -> list[Complaint]:
        complaints = await self.complaint_repo.get_complaints(filters)
        return complaints

    async def get_complaint_by_id(
            self,
            complaint_id: int
    ) -> Complaint:
        result = await self.complaint_repo.get_complaint_by_id(complaint_id)
        if not result:
            raise ComplaintNotFoundError("Complaint not found")
        return result