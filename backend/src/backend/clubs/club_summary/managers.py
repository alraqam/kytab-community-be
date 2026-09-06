from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.services import is_club_member
from src.backend.clubs.club_summary.schemas import GetClubSummary
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.events.repository.event import ClubEventRepository
from src.backend.clubs.thread.repository.posts import PostRepository
from src.backend.clubs.thread.repository.thread import ThreadRepository
from src.backend.identity.auth.models import User


class ClubSummaryManager:
    """Builds a member-facing summary of a club's membership, latest post, and next event."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.membership_repo = ClubMembershipRepository(session)
        self.thread_repo = ThreadRepository(session)
        self.post_repo = PostRepository(session)
        self.event_repo = ClubEventRepository(session)

    async def get_club_summary(
            self,
            user: User,
            club: Club,
    ) -> GetClubSummary:
        """Builds a summary of a club's member count, latest general post, and next upcoming event.

        Args:
            user: User requesting the summary; must be a club member.
            club: Club to summarize.

        Returns:
            GetClubSummary with member count and latest post/next event, when present.

        Raises:
            NotClubMemberError: When the user is not a member of the club.
        """
        await is_club_member(club, user, self.session)

        memberships = await self.membership_repo.get_memberships(club)

        threads = await self.thread_repo.get_club_general_threads(club.id)
        latest_post = None
        for thread in threads:
            posts = await self.post_repo.get_posts(thread.id)
            for post in posts:
                if latest_post is None or post.created_at > latest_post.created_at:
                    latest_post = post

        future_events = await self.event_repo.get_club_future_events(club.id)
        next_event = min(future_events, key=lambda event: event.start_at) if future_events else None

        return GetClubSummary(
            club_id=club.id,
            club_name=club.name,
            member_count=len(memberships),
            latest_post_title=latest_post.title if latest_post else None,
            latest_post_created_at=latest_post.created_at if latest_post else None,
            latest_post_author_username=latest_post.author_username if latest_post else None,
            next_event_title=next_event.title if next_event else None,
            next_event_start_at=next_event.start_at if next_event else None,
        )
