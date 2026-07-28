from fastapi import FastAPI

from src.backend.core.exceptions import Unauthorized, Forbidden, NotFound, Conflict, BadRequest, ServiceUnavailable
from src.backend.core.handlers import unauthorized_exception_handler, forbidden_exception_handler, \
    not_found_exception_handler, conflict_exception_handler, bad_request_exception_handler, \
    service_unavailable_exception_handler


from src.backend.identity.auth.routers.auth import router as auth_router
from src.backend.identity.auth.routers.session import router as session_router
from src.backend.identity.users.routers import router as user_router
from src.backend.identity.profile.routers import router as profile_router
from src.backend.identity.blocked_users.routers import router as blocked_users_router
from src.backend.identity.follow.routers import router as follow_router
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
from src.backend.clubs.clubs.routers.public import router as clubs_public_router
from src.backend.clubs.clubs.routers.admin import router as clubs_admin_router
from src.backend.clubs.club_membership.routers.membership import router as membership_router
from src.backend.clubs.club_membership.routers.requests import router as request_router
from src.backend.clubs.club_membership.routers.invitation import router as invitation_router
from src.backend.clubs.club_membership.routers.user_membership import router as user_membership_router
from src.backend.clubs.club_membership.routers.block import router as club_block_router
from src.backend.clubs.reading_session.routers.session import router as reading_sessions_router
from src.backend.clubs.reading_session.routers.milestone import router as milestone_router


app = FastAPI(
    version="1.0.0",
    redirect_slashes=False,
)

clubs_public_router.include_router(club_block_router)
reading_sessions_router.include_router(milestone_router)
clubs_public_router.include_router(reading_sessions_router)
reading_period_router.include_router(progress_logs_router)
shelf_item_router.include_router(reading_period_router)
shelf_router.include_router(shelf_item_router)
review_router.include_router(review_comments_router)
review_router.include_router(review_like_router)
work_router.include_router(review_router)
clubs_public_router.include_router(membership_router)

app.include_router(auth_router)
app.include_router(session_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(blocked_users_router)
app.include_router(follow_router)
app.include_router(books_router)
app.include_router(work_router)
app.include_router(librarian_work_router)
app.include_router(author_router)
app.include_router(librarian_author_router)
app.include_router(edition_router)
app.include_router(librarian_edition_router)
app.include_router(series_router)
app.include_router(librarian_series_router)
app.include_router(genre_router)
app.include_router(librarian_genre_router)
app.include_router(librarian_submission_public_router)
app.include_router(librarian_submission_router)
app.include_router(reading_goals_router)
app.include_router(shelf_router)
app.include_router(user_progress_router)
app.include_router(clubs_public_router)
app.include_router(clubs_admin_router)
app.include_router(user_membership_router)
app.include_router(invitation_router)
app.include_router(request_router)

app.add_exception_handler(Unauthorized, unauthorized_exception_handler)
app.add_exception_handler(Forbidden, forbidden_exception_handler)
app.add_exception_handler(NotFound, not_found_exception_handler)
app.add_exception_handler(Conflict, conflict_exception_handler)
app.add_exception_handler(BadRequest, bad_request_exception_handler)
app.add_exception_handler(ServiceUnavailable, service_unavailable_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)