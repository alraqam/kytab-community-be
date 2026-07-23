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


app = FastAPI(
    version="1.0.0",
    redirect_slashes=False,
)

shelf_router.include_router(shelf_item_router)

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

app.add_exception_handler(Unauthorized, unauthorized_exception_handler)
app.add_exception_handler(Forbidden, forbidden_exception_handler)
app.add_exception_handler(NotFound, not_found_exception_handler)
app.add_exception_handler(Conflict, conflict_exception_handler)
app.add_exception_handler(BadRequest, bad_request_exception_handler)
app.add_exception_handler(ServiceUnavailable, service_unavailable_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)