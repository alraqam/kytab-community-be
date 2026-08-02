from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.thread.managers.posts import PostManager
from src.backend.identity.auth.models import User
from src.backend.identity.users.managers import UserManager
from src.backend.identity.users.schemas import UpdateUserActivity
from src.backend.library.reviews.managers.comments import ReviewCommentManager
from src.backend.library.reviews.managers.review import ReviewManager
from src.backend.trust_safety.complaint.exceptions import ComplaintStatusError, ComplaintNotFoundError, \
    InvalidComplaintActionError
from src.backend.trust_safety.complaint.filters import ComplaintFilter
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.complaint.repository import ComplaintRepository
from src.backend.trust_safety.complaint.schemas import CreateComplaint, ComplaintObjectType, ComplaintStatus, \
    WarnComplaintTarget
from src.backend.notifications.managers.notification import NotificationManager
from src.backend.notifications.schemas import NotificationCategory, NotificationObjectType


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
        self.post_manager = PostManager(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)


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
            case ComplaintObjectType.post:
                await self.post_manager.get_post_by_id(request.object_id)
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

        reporter = await self.user_manager.get_user_by_id(complaint.reporter_id)
        await self.notification_manager.notify(
            reporter,
            category=NotificationCategory.general,
            title="Your report has been reviewed",
            object_type=NotificationObjectType.complaint,
            object_id=complaint.id,
        )

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

        reporter = await self.user_manager.get_user_by_id(complaint.reporter_id)
        await self.notification_manager.notify(
            reporter,
            category=NotificationCategory.general,
            title="Your report has been dismissed",
            object_type=NotificationObjectType.complaint,
            object_id=complaint.id,
        )

    async def _get_target_user(
            self,
            complaint: Complaint,
    ) -> User:
        match complaint.object_type:
            case ComplaintObjectType.review:
                review = await self.review_manager.get_review_by_id(complaint.object_id)
                return await self.user_manager.get_user_by_id(review.user_id)
            case ComplaintObjectType.comment:
                comment = await self.comment_manager.get_comment_by_id(complaint.object_id)
                return await self.user_manager.get_user_by_id(comment.user_id)
            case ComplaintObjectType.post:
                post = await self.post_manager.get_post_by_id(complaint.object_id)
                return await self.user_manager.get_user_by_id(post.author_id)
            case ComplaintObjectType.club:
                club = await self.club_manager.get_club_by_id(complaint.object_id)
                return await self.user_manager.get_user_by_id(club.owner_id)
            case ComplaintObjectType.user:
                return await self.user_manager.get_user_by_id(complaint.object_id)

    async def remove_complaint_content(
            self,
            user: User,
            complaint: Complaint,
    ) -> None:
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        match complaint.object_type:
            case ComplaintObjectType.review:
                review = await self.review_manager.get_review_by_id(complaint.object_id)
                await self.review_manager.admin_delete_review(user, review)
            case ComplaintObjectType.comment:
                comment = await self.comment_manager.get_comment_by_id(complaint.object_id)
                await self.comment_manager.delete_user_comment(user, comment)
            case ComplaintObjectType.post:
                post = await self.post_manager.get_post_by_id(complaint.object_id)
                await self.post_manager.admin_delete_post(user, post)
            case _:
                raise InvalidComplaintActionError("Only reviews, comments, and posts support content removal")

        await self.resolve_complaint(user, complaint)

    async def warn_complaint_target(
            self,
            user: User,
            complaint: Complaint,
            request: WarnComplaintTarget,
    ) -> None:
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        target = await self._get_target_user(complaint)
        await self.notification_manager.notify(
            target,
            category=NotificationCategory.general,
            title="You received a moderation warning",
            body=request.message,
            object_type=NotificationObjectType.complaint,
            object_id=complaint.id,
        )
        await self.resolve_complaint(user, complaint)

    async def suspend_complaint_target(
            self,
            user: User,
            complaint: Complaint,
    ) -> None:
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        target = await self._get_target_user(complaint)
        await self.user_manager.update_user_activity(target, UpdateUserActivity(is_active=False))
        await self.resolve_complaint(user, complaint)

    async def ban_complaint_target(
            self,
            user: User,
            complaint: Complaint,
    ) -> None:
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        target = await self._get_target_user(complaint)
        await self.user_manager.delete_user(target)
        await self.resolve_complaint(user, complaint)

    async def get_club_complaints(
            self,
            user: User,
            club: Club,
    ) -> list[Complaint]:
        is_owner_or_moderator(club, user.id)
        return await self.complaint_repo.get_club_complaints(club.id)

    async def escalate_complaint(
            self,
            user: User,
            club: Club,
            complaint: Complaint,
    ) -> None:
        is_owner_or_moderator(club, user.id)

        club_complaints = await self.complaint_repo.get_club_complaints(club.id)
        if complaint.id not in [c.id for c in club_complaints]:
            raise ComplaintNotFoundError("Complaint not found in this club")

        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        await self.complaint_repo.update_escalated(complaint, True)
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