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

app = FastAPI(
    version="1.0.0",
    redirect_slashes=False,
)

app.include_router(auth_router)
app.include_router(session_router)
app.include_router(user_router)
app.include_router(profile_router)
app.include_router(blocked_users_router)
app.include_router(follow_router)


app.add_exception_handler(Unauthorized, unauthorized_exception_handler)
app.add_exception_handler(Forbidden, forbidden_exception_handler)
app.add_exception_handler(NotFound, not_found_exception_handler)
app.add_exception_handler(Conflict, conflict_exception_handler)
app.add_exception_handler(BadRequest, bad_request_exception_handler)
app.add_exception_handler(ServiceUnavailable, service_unavailable_exception_handler)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)