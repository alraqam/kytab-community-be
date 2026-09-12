"""FastAPI application entrypoint: wires up all feature routers and global exception handlers."""

from fastapi import APIRouter, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import IntegrityError

from src.backend.core.exceptions import Unauthorized, Forbidden, NotFound, Conflict, BadRequest, ServiceUnavailable, \
    TooManyRequests
from src.backend.core.handlers import unauthorized_exception_handler, forbidden_exception_handler, \
    not_found_exception_handler, conflict_exception_handler, bad_request_exception_handler, \
    service_unavailable_exception_handler, too_many_requests_exception_handler, integrity_error_exception_handler


from src.backend.identity.auth.routers.auth import router as auth_router
from src.backend.identity.auth.routers.session import router as session_router
from src.backend.identity.auth.routers.two_factor import router as two_factor_router
from src.backend.identity.users.routers import router as user_router
from src.backend.identity.profile.routers import router as profile_router
from src.backend.identity.blocked_users.routers import router as blocked_users_router
from src.backend.identity.follow.routers import router as follow_router
from src.backend.identity.analytics.routers.public import router as user_analytics_router
from src.backend.identity.analytics.routers.admin import router as user_analytics_admin_router
from src.backend.identity.feed.routers import router as feed_router

from src.backend.catalog.books.routers.books import router as books_router
from src.backend.catalog.books.routers.work import router as work_router
from src.backend.catalog.books.routers.author import router as author_router
from src.backend.catalog.books.routers.edition import router as edition_router
from src.backend.catalog.books.routers.series import router as series_router
from src.backend.catalog.books.routers.genre import router as genre_router
from src.backend.catalog.librarian.routers.submission import router as librarian_submission_router
from src.backend.catalog.librarian.routers.public import router as librarian_submission_public_router
from src.backend.catalog.librarian.routers.authors import router as librarian_author_router
from src.backend.catalog.librarian.routers.edition import router as librarian_edition_router
from src.backend.catalog.librarian.routers.genre import router as librarian_genre_router
from src.backend.catalog.librarian.routers.series import router as librarian_series_router
from src.backend.catalog.librarian.routers.work import router as librarian_work_router

from src.backend.library.reading_goals.routers import router as reading_goals_router
from src.backend.library.shelf.routers.shelf import router as shelf_router
from src.backend.library.shelf.routers.shelf_item import router as shelf_item_router
from src.backend.library.reviews.routers.review import router as review_router
from src.backend.library.reviews.routers.comments import router as review_comments_router
from src.backend.library.reviews.routers.like import router as review_like_router
from src.backend.library.progress.routers.reading_period import router as reading_period_router
from src.backend.library.progress.routers.progress_logs import router as progress_logs_router
from src.backend.library.progress.routers.users_progress import router as user_progress_router
from src.backend.library.goodreads_import.routers import router as goodreads_import_router

from src.backend.clubs.clubs.routers.public import router as clubs_public_router
from src.backend.clubs.clubs.routers.admin import router as clubs_admin_router
from src.backend.clubs.club_membership.routers.membership import router as membership_router
from src.backend.clubs.club_membership.routers.requests import router as request_router
from src.backend.clubs.club_membership.routers.invitation import router as invitation_router
from src.backend.clubs.club_membership.routers.user_membership import router as user_membership_router
from src.backend.clubs.club_membership.routers.block import router as club_block_router
from src.backend.clubs.reading_session.routers.session import router as reading_sessions_router
from src.backend.clubs.reading_session.routers.milestone import router as milestone_router
from src.backend.clubs.reading_session.routers.progress import router as milestone_progress_router
from src.backend.clubs.reading_session.routers.prompt import router as discussion_prompt_router
from src.backend.clubs.thread.routers.thread_general import router as thread_general_router
from src.backend.clubs.thread.routers.thread_session import router as thread_session_router
from src.backend.clubs.thread.routers.posts_general import router as post_general_router
from src.backend.clubs.thread.routers.posts_session import router as post_session_router
from src.backend.clubs.thread.routers.reaction_session import router as reaction_session_router
from src.backend.clubs.thread.routers.reaction_general import router as reaction_general_router
from src.backend.clubs.voting.routers.voting_poll import router as voting_poll_router
from src.backend.clubs.voting.routers.poll_candidate import router as poll_candidate_router
from src.backend.clubs.voting.routers.vote_poll import router as vote_poll_router
from src.backend.clubs.events.routers.event import router as event_router
from src.backend.clubs.events.routers.rsvp import router as event_rsvp_router
from src.backend.clubs.analytics.routers.public import router as club_analytics_router
from src.backend.clubs.analytics.routers.admin import router as club_analytics_admin_router
from src.backend.clubs.club_summary.routers import router as club_summary_router

from src.backend.trust_safety.audit_log.routers.admin import router as audit_log_admin_router
from src.backend.trust_safety.complaint.routers.public import router as public_complaint_router
from src.backend.trust_safety.complaint.routers.admin import router as admin_complaint_router
from src.backend.trust_safety.complaint.routers.club import router as club_complaint_router
from src.backend.trust_safety.consent.routers.document import router as document_router
from src.backend.trust_safety.consent.routers.consent import router as consent_router
from src.backend.trust_safety.export.routers import router as export_router

from src.backend.notifications.routers.preference import router as preference_router
from src.backend.notifications.routers.notification import router as notification_router
from src.backend.notifications.routers.push import router as push_subscription_router

from src.backend.administration.announcements.routers.admin import router as announcement_admin_router
from src.backend.administration.announcements.routers.public import router as announcement_public_router
from src.backend.administration.feature_flags.routers.admin import router as feature_flag_admin_router
from src.backend.administration.feature_flags.routers.public import router as feature_flag_public_router


app = FastAPI(
    version="1.0.0",
    redirect_slashes=False,
)

Instrumentator().instrument(app).expose(app)


api_v1_router = APIRouter(prefix="/api/v1")

post_general_router.include_router(reaction_general_router)
thread_general_router.include_router(post_general_router)
clubs_public_router.include_router(thread_general_router)
post_session_router.include_router(reaction_session_router)
thread_session_router.include_router(post_session_router)
milestone_router.include_router(thread_session_router)
milestone_router.include_router(milestone_progress_router)
milestone_router.include_router(discussion_prompt_router)
reading_sessions_router.include_router(milestone_router)
clubs_public_router.include_router(reading_sessions_router)
reading_period_router.include_router(progress_logs_router)
shelf_item_router.include_router(reading_period_router)
shelf_router.include_router(shelf_item_router)
review_router.include_router(review_comments_router)
review_router.include_router(review_like_router)
work_router.include_router(review_router)
clubs_public_router.include_router(membership_router)
clubs_public_router.include_router(club_block_router)
clubs_public_router.include_router(club_complaint_router)
voting_poll_router.include_router(poll_candidate_router)
voting_poll_router.include_router(vote_poll_router)
clubs_public_router.include_router(voting_poll_router)
event_router.include_router(event_rsvp_router)
clubs_public_router.include_router(event_router)
clubs_public_router.include_router(club_analytics_router)
clubs_public_router.include_router(club_summary_router)

api_v1_router.include_router(auth_router)
api_v1_router.include_router(session_router)
api_v1_router.include_router(two_factor_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(blocked_users_router)
api_v1_router.include_router(follow_router)
api_v1_router.include_router(feed_router)
api_v1_router.include_router(user_analytics_router)
api_v1_router.include_router(user_analytics_admin_router)
api_v1_router.include_router(books_router)
api_v1_router.include_router(work_router)
api_v1_router.include_router(librarian_work_router)
api_v1_router.include_router(author_router)
api_v1_router.include_router(librarian_author_router)
api_v1_router.include_router(edition_router)
api_v1_router.include_router(librarian_edition_router)
api_v1_router.include_router(series_router)
api_v1_router.include_router(librarian_series_router)
api_v1_router.include_router(genre_router)
api_v1_router.include_router(librarian_genre_router)
api_v1_router.include_router(librarian_submission_public_router)
api_v1_router.include_router(librarian_submission_router)
api_v1_router.include_router(reading_goals_router)
api_v1_router.include_router(shelf_router)
api_v1_router.include_router(user_progress_router)
api_v1_router.include_router(goodreads_import_router)
api_v1_router.include_router(clubs_public_router)
api_v1_router.include_router(clubs_admin_router)
api_v1_router.include_router(club_analytics_admin_router)
api_v1_router.include_router(user_membership_router)
api_v1_router.include_router(invitation_router)
api_v1_router.include_router(request_router)
api_v1_router.include_router(public_complaint_router)
api_v1_router.include_router(admin_complaint_router)
api_v1_router.include_router(audit_log_admin_router)
api_v1_router.include_router(document_router)
api_v1_router.include_router(consent_router)
api_v1_router.include_router(export_router)
api_v1_router.include_router(preference_router)
api_v1_router.include_router(notification_router)
api_v1_router.include_router(push_subscription_router)

api_v1_router.include_router(announcement_admin_router)
api_v1_router.include_router(announcement_public_router)
api_v1_router.include_router(feature_flag_admin_router)
api_v1_router.include_router(feature_flag_public_router)

app.include_router(api_v1_router)

app.add_exception_handler(Unauthorized, unauthorized_exception_handler)
app.add_exception_handler(Forbidden, forbidden_exception_handler)
app.add_exception_handler(NotFound, not_found_exception_handler)
app.add_exception_handler(Conflict, conflict_exception_handler)
app.add_exception_handler(BadRequest, bad_request_exception_handler)
app.add_exception_handler(ServiceUnavailable, service_unavailable_exception_handler)
app.add_exception_handler(TooManyRequests, too_many_requests_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)