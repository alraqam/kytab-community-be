"""Import every ORM model so SQLAlchemy's mapper registry is fully populated
before any mapper configuration is triggered (Celery worker, Alembic, etc.)."""

from src.backend.administration.announcements.models import Announcement
from src.backend.catalog.books.models import Work, Edition, Genre, WorkGenre, Author, WorkAuthor, Series, WorkSeries
from src.backend.catalog.librarian.models import LibrarianSubmission
from src.backend.clubs.club_membership.models import ClubMembership, ClubBlocked, ClubJoinRequest, ClubInvitation
from src.backend.clubs.clubs.models import Club, ClubGenre
from src.backend.clubs.events.models import EventRSVP, ClubEvent
from src.backend.clubs.reading_session.models import ReadingSession, Milestone, MilestoneProgress, DiscussionPrompt
from src.backend.clubs.thread.models import Thread, Post, PostReaction
from src.backend.clubs.voting.models import VotingPoll, PollVote, PollCandidate
from src.backend.identity.auth.models import User, Session
from src.backend.identity.blocked_users.models import BlockedUser
from src.backend.identity.follow.models import Follow
from src.backend.identity.profile.models import Profile
from src.backend.library.goodreads_import.models import GoodreadsImportRow
from src.backend.library.progress.models import ProgressLog, ReadingPeriod
from src.backend.library.reading_goals.models import ReadingGoal
from src.backend.library.reviews.models import Review, ReviewLike, ReviewComment
from src.backend.library.shelf.models import Shelf, ShelfItem
from src.backend.notifications.models import Notification, NotificationPreference
from src.backend.trust_safety.audit_log.models import AuditLog
from src.backend.trust_safety.complaint.models import Complaint
from src.backend.trust_safety.consent.models import ConsentRecords, LegalDocument
