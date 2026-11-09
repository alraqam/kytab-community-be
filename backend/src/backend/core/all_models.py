"""Import every ORM model so SQLAlchemy's mapper registry is fully populated
before any mapper configuration is triggered (Celery worker, Alembic, etc.)."""

from src.backend.administration.announcements.models.announcement import Announcement
from src.backend.administration.feature_flags.models.feature_flag import FeatureFlag
from src.backend.catalog.books.models.book import Work, Edition, Genre, WorkGenre, Author, WorkAuthor, Series, WorkSeries
from src.backend.catalog.librarian.models.librarian import LibrarianSubmission
from src.backend.clubs.club_membership.models.membership import ClubMembership, ClubBlocked, ClubJoinRequest, ClubInvitation
from src.backend.clubs.clubs.models.club import Club, ClubGenre
from src.backend.clubs.events.models.event import EventRSVP, ClubEvent
from src.backend.clubs.reading_session.models.reading_session import ReadingSession, Milestone, MilestoneProgress, DiscussionPrompt
from src.backend.clubs.thread.models.thread import Thread, Post, PostReaction
from src.backend.clubs.voting.models.voting import VotingPoll, PollVote, PollCandidate
from src.backend.identity.auth.models.auth import User, Session
from src.backend.identity.blocked_users.models.blocked_user import BlockedUser
from src.backend.identity.follow.models.follow import Follow
from src.backend.identity.profile.models.profile import Profile
from src.backend.library.goodreads_import.models.goodreads_import import GoodreadsImportRow
from src.backend.library.progress.models.progress import ProgressLog, ReadingPeriod
from src.backend.library.reading_goals.models.reading_goal import ReadingGoal
from src.backend.library.reviews.models.review import Review, ReviewLike, ReviewComment
from src.backend.library.shelf.models.shelf import Shelf, ShelfItem
from src.backend.notifications.models.notification import Notification, NotificationPreference
from src.backend.trust_safety.audit_log.models.audit_log import AuditLog
from src.backend.trust_safety.complaint.models.complaint import Complaint
from src.backend.trust_safety.consent.models.consent import ConsentRecords, LegalDocument
