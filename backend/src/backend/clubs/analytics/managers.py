from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.analytics.schemas import ClubModerationSummary, GetClubAnalytics, GetPlatformClubAnalytics, \
    MemberRoleBreakdown, MonthlyCount
from src.backend.clubs.club_membership.managers.requests import ClubJoinRequestManager
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.schemas import MemberRole
from src.backend.clubs.club_membership.services import is_owner_or_moderator
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.repository import ClubRepository
from src.backend.clubs.clubs.schemas import ClubTypes
from src.backend.clubs.events.repository.event import ClubEventRepository
from src.backend.clubs.events.repository.rsvp import EventRSVPRepository
from src.backend.clubs.reading_session.repository.progress import MilestoneProgressRepository
from src.backend.clubs.reading_session.repository.session import ReadingSessionRepository
from src.backend.clubs.reading_session.schemas import ReadingSessionStatus
from src.backend.clubs.thread.repository.posts import PostRepository
from src.backend.clubs.thread.repository.thread import ThreadRepository
from src.backend.clubs.voting.repositories.vote_poll import VotePollRepository
from src.backend.clubs.voting.repositories.voting_poll import VotingPollRepository
from src.backend.identity.auth.models import User
from src.backend.trust_safety.complaint.schemas import ComplaintStatus


class ClubAnalyticsManager:
    """Aggregates club-level and platform-wide club analytics from existing club domain data."""

    def __init__(
            self,
            session: AsyncSession
    ):
        from src.backend.trust_safety.complaint.managers import ComplaintManager

        self.session = session
        self.club_repo = ClubRepository(session)
        self.membership_repo = ClubMembershipRepository(session)
        self.thread_repo = ThreadRepository(session)
        self.post_repo = PostRepository(session)
        self.session_repo = ReadingSessionRepository(session)
        self.progress_repo = MilestoneProgressRepository(session)
        self.poll_repo = VotingPollRepository(session)
        self.vote_repo = VotePollRepository(session)
        self.event_repo = ClubEventRepository(session)
        self.rsvp_repo = EventRSVPRepository(session)
        self.join_request_manager = ClubJoinRequestManager(session)
        self.complaint_manager = ComplaintManager(session)

    async def get_moderation_summary(
            self,
            user: User,
            club: Club,
    ) -> ClubModerationSummary:
        """Builds a moderation summary of pending join requests and complaints for a club.

        Args:
            user: User requesting the summary; must be an owner or moderator.
            club: Club to summarize.

        Returns:
            ClubModerationSummary with pending join request and complaint counts.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator of the club.
        """
        join_requests = await self.join_request_manager.get_club_requests(user, club)
        complaints = await self.complaint_manager.get_club_complaints(user, club)
        pending_complaints = [c for c in complaints if c.status == ComplaintStatus.pending]

        return ClubModerationSummary(
            pending_join_requests=len(join_requests),
            pending_complaints=len(pending_complaints),
            total_complaints=len(complaints),
        )

    async def get_club_overview(
            self,
            user: User,
            club: Club,
    ) -> GetClubAnalytics:
        """Builds an analytics overview of a club's membership, activity, and engagement.

        Args:
            user: User requesting the overview; must be an owner or moderator.
            club: Club to analyze.

        Returns:
            GetClubAnalytics with membership, thread, reading session, poll, and event statistics.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator of the club.
        """
        is_owner_or_moderator(club, user.id)

        memberships = await self.membership_repo.get_memberships(club)
        role_counts = Counter(membership.role for membership in memberships)
        growth = Counter(membership.created_at.strftime("%Y-%m") for membership in memberships)

        general_threads = await self.thread_repo.get_club_general_threads(club.id)
        general_posts_count = 0
        for thread in general_threads:
            posts = await self.post_repo.get_posts(thread.id)
            general_posts_count += len(posts)

        sessions = await self.session_repo.get_club_sessions(club.id)
        active_sessions = [s for s in sessions if s.status == ReadingSessionStatus.active]
        completed_sessions = [s for s in sessions if s.status == ReadingSessionStatus.completed]

        completion_ratios = []
        for session in active_sessions:
            progresses = await self.progress_repo.get_session_milestone_progress(session.id)
            if progresses:
                finished = sum(1 for progress in progresses if progress.is_finished)
                completion_ratios.append(finished / len(progresses))
        average_milestone_completion = (
            sum(completion_ratios) / len(completion_ratios) if completion_ratios else None
        )

        polls = await self.poll_repo.get_club_polls(club.id)

        events = await self.event_repo.get_club_events(club.id)
        future_events = await self.event_repo.get_club_future_events(club.id)

        return GetClubAnalytics(
            club_id=club.id,
            total_members=len(memberships),
            role_breakdown=MemberRoleBreakdown(
                owner=role_counts.get(MemberRole.club_owner, 0),
                moderator=role_counts.get(MemberRole.club_moderator, 0),
                member=role_counts.get(MemberRole.member, 0),
            ),
            member_growth=[
                MonthlyCount(month=month, count=count)
                for month, count in sorted(growth.items())
            ],
            general_threads_count=len(general_threads),
            general_posts_count=general_posts_count,
            active_reading_sessions=len(active_sessions),
            completed_reading_sessions=len(completed_sessions),
            average_milestone_completion=average_milestone_completion,
            polls_count=len(polls),
            events_count=len(events),
            upcoming_events_count=len(future_events),
        )

    async def get_platform_analytics(self) -> GetPlatformClubAnalytics:
        """Aggregates platform-wide statistics across all clubs.

        Returns:
            GetPlatformClubAnalytics with club counts by type/status and membership totals.
        """
        clubs = await self.club_repo.get_all_clubs()

        type_counts = Counter(club.club_type for club in clubs)
        archived_count = sum(1 for club in clubs if club.is_archived)
        growth = Counter(club.created_at.strftime("%Y-%m") for club in clubs)

        total_memberships = 0
        for club in clubs:
            memberships = await self.membership_repo.get_memberships(club)
            total_memberships += len(memberships)

        return GetPlatformClubAnalytics(
            total_clubs=len(clubs),
            active_clubs=len(clubs) - archived_count,
            archived_clubs=archived_count,
            public_clubs=type_counts.get(ClubTypes.public, 0),
            private_clubs=type_counts.get(ClubTypes.private, 0),
            secret_clubs=type_counts.get(ClubTypes.secret, 0),
            total_memberships=total_memberships,
            clubs_created_by_month=[
                MonthlyCount(month=month, count=count)
                for month, count in sorted(growth.items())
            ],
        )
