from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.managers import ClubManager
from src.backend.core.storage import StorageService
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
    """Handles complaint business logic: filing, moderation review, and enforcement actions against reported content/users."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.complaint_repo = ComplaintRepository(session)
        self.review_manager = ReviewManager(session)
        self.club_manager = ClubManager(session, StorageService())
        self.comment_manager = ReviewCommentManager(session)
        self.post_manager = PostManager(session)
        self.user_manager = UserManager(session)
        self.notification_manager = NotificationManager(session)


    async def create_compliant(
            self,
            user: User,
            request: CreateComplaint,
    ) -> Complaint:
        """Files a new complaint after verifying the reported object exists.

        Args:
            user: User filing the complaint.
            request: CreateComplaint payload with the target object and category.

        Returns:
            Newly created Complaint instance.
        """
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
        return await self.complaint_repo.get_complaint_by_id(result.id)

    async def _mark_resolved(
            self,
            user: User,
            complaint: Complaint,
            status: str,
            notification_title: str,
    ) -> None:
        """Stamps a complaint resolved with the given status and notifies the reporter.

        Args:
            user: Moderator resolving the complaint.
            complaint: Complaint instance to resolve.
            status: Terminal status to apply (reviewed or dismissed).
            notification_title: Title of the notification sent to the reporter.
        """
        await self.complaint_repo.resolve_complaint(
            user_id=user.id,
            complaint=complaint
        )
        await self.complaint_repo.update_complaint_status(complaint, status)
        await self.session.commit()

        reporter = await self.user_manager.get_user_by_id(complaint.reporter_id)
        await self.notification_manager.notify(
            reporter,
            category=NotificationCategory.general,
            title=notification_title,
            object_type=NotificationObjectType.complaint,
            object_id=complaint.id,
        )

    async def resolve_complaint(
            self,
            user: User,
            complaint: Complaint
    ) -> None:
        """Marks a pending complaint as reviewed and notifies the reporter.

        Args:
            user: Moderator resolving the complaint.
            complaint: Complaint instance to resolve.

        Raises:
            ComplaintStatusError: When the complaint is not pending.
        """
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")
        await self._mark_resolved(user, complaint, ComplaintStatus.reviewed, "Your report has been reviewed")

    async def dismiss_complaint(
            self,
            user: User,
            complaint: Complaint
    ) -> None:
        """Marks a pending complaint as dismissed and notifies the reporter.

        Args:
            user: Moderator dismissing the complaint.
            complaint: Complaint instance to dismiss.

        Raises:
            ComplaintStatusError: When the complaint is not pending.
        """
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")
        await self._mark_resolved(user, complaint, ComplaintStatus.dismissed, "Your report has been dismissed")

    async def _get_target_user(
            self,
            complaint: Complaint,
    ) -> User:
        """Resolves the user who owns/authored the content a complaint targets, or the reported user directly.

        Args:
            complaint: Complaint to resolve the target user for.

        Returns:
            User instance the complaint's moderation actions should apply to.
        """
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
        """Deletes the reported content (review, comment, or post) and resolves the complaint.

        Args:
            user: Moderator performing the removal.
            complaint: Complaint whose reported content should be removed.

        Raises:
            ComplaintStatusError: When the complaint is not pending.
            InvalidComplaintActionError: When the complaint's object type doesn't support content removal.
        """
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

        await self._mark_resolved(user, complaint, ComplaintStatus.reviewed, "Your report has been reviewed")

    async def warn_complaint_target(
            self,
            user: User,
            complaint: Complaint,
            request: WarnComplaintTarget,
    ) -> None:
        """Sends a moderation warning notification to a complaint's target and resolves the complaint.

        Args:
            user: Moderator issuing the warning.
            complaint: Complaint whose target should be warned.
            request: WarnComplaintTarget payload with the warning message.

        Raises:
            ComplaintStatusError: When the complaint is not pending.
        """
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
        await self._mark_resolved(user, complaint, ComplaintStatus.reviewed, "Your report has been reviewed")

    async def suspend_complaint_target(
            self,
            user: User,
            complaint: Complaint,
    ) -> None:
        """Deactivates a complaint's target user and resolves the complaint.

        Args:
            user: Moderator performing the suspension.
            complaint: Complaint whose target should be suspended.

        Raises:
            ComplaintStatusError: When the complaint is not pending.
        """
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        target = await self._get_target_user(complaint)
        await self.user_manager.update_user_activity(target, UpdateUserActivity(is_active=False))
        await self._mark_resolved(user, complaint, ComplaintStatus.reviewed, "Your report has been reviewed")

    async def ban_complaint_target(
            self,
            user: User,
            complaint: Complaint,
    ) -> None:
        """Deletes a complaint's target user account and resolves the complaint.

        Args:
            user: Moderator performing the ban.
            complaint: Complaint whose target should be banned.

        Raises:
            ComplaintStatusError: When the complaint is not pending.
        """
        if complaint.status != ComplaintStatus.pending:
            raise ComplaintStatusError("Complaint status error")

        target = await self._get_target_user(complaint)
        await self.user_manager.delete_user(target)
        await self._mark_resolved(user, complaint, ComplaintStatus.reviewed, "Your report has been reviewed")

    async def get_club_complaints(
            self,
            user: User,
            club: Club,
    ) -> list[Complaint]:
        """Lists complaints filed within a club, for club owners/moderators.

        Args:
            user: User requesting the complaints; must own or moderate the club.
            club: Club to fetch complaints for.

        Returns:
            List of Complaint instances filed against the club or its content.

        Raises:
            IsNotClubOwnerError: When the user is neither the club owner nor a moderator.
        """
        is_owner_or_moderator(club, user.id)
        return await self.complaint_repo.get_club_complaints(club.id)

    async def escalate_complaint(
            self,
            user: User,
            club: Club,
            complaint: Complaint,
    ) -> None:
        """Escalates a club-level complaint to platform moderation.

        Args:
            user: User escalating the complaint; must own or moderate the club.
            club: Club the complaint belongs to.
            complaint: Complaint instance to escalate.

        Raises:
            IsNotClubOwnerError: When the user is neither the club owner nor a moderator.
            ComplaintNotFoundError: When the complaint does not belong to this club.
            ComplaintStatusError: When the complaint is not pending.
        """
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
        """Lists complaints matching the given filters.

        Args:
            filters: ComplaintFilter with search, type, category, status, and escalation criteria.

        Returns:
            List of matching Complaint instances.
        """
        complaints = await self.complaint_repo.get_complaints(filters)
        return complaints

    async def get_complaint_by_id(
            self,
            complaint_id: int
    ) -> Complaint:
        """Fetches a single complaint by ID.

        Args:
            complaint_id: ID of the complaint to fetch.

        Returns:
            Matching Complaint instance.

        Raises:
            ComplaintNotFoundError: When no complaint matches the ID.
        """
        result = await self.complaint_repo.get_complaint_by_id(complaint_id)
        if not result:
            raise ComplaintNotFoundError("Complaint not found")
        return result