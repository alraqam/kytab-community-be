from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.backend.core.exceptions import Conflict, NotFound, Forbidden, Unauthorized, BadRequest, ServiceUnavailable, \
    TooManyRequests


async def unauthorized_exception_handler(request: Request, exc: Unauthorized):
    """Converts Unauthorized exceptions to HTTP 401 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised Unauthorized exception.

    Returns:
        JSONResponse with status 401 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=
        {
            "detail": str(exc),
        },
    )


async def forbidden_exception_handler(request: Request, exc: Forbidden):
    """Converts Forbidden exceptions to HTTP 403 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised Forbidden exception.

    Returns:
        JSONResponse with status 403 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=
        {
            "detail": str(exc),
        },
    )

async def not_found_exception_handler(request: Request, exc: NotFound):
    """Converts NotFound exceptions to HTTP 404 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised NotFound exception.

    Returns:
        JSONResponse with status 404 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=
        {
            "detail": str(exc),
        },
    )


async def conflict_exception_handler(request: Request, exc: Conflict):
    """Converts Conflict exceptions to HTTP 409 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised Conflict exception.

    Returns:
        JSONResponse with status 409 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=
        {
            "detail": str(exc),
        },
    )

async def bad_request_exception_handler(request: Request, exc: BadRequest):
    """Converts BadRequest exceptions to HTTP 400 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised BadRequest exception.

    Returns:
        JSONResponse with status 400 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=
        {
            "detail": str(exc),
        },
    )


async def service_unavailable_exception_handler(request: Request, exc: ServiceUnavailable):
    """Converts ServiceUnavailable exceptions to HTTP 503 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised ServiceUnavailable exception.

    Returns:
        JSONResponse with status 503 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=
        {
            "detail": str(exc),
        },
    )


async def too_many_requests_exception_handler(request: Request, exc: TooManyRequests):
    """Converts TooManyRequests exceptions to HTTP 429 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised TooManyRequests exception.

    Returns:
        JSONResponse with status 429 and exception message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=
        {
            "detail": str(exc),
        },
    )


async def integrity_error_exception_handler(request: Request, exc: IntegrityError):
    """Converts unhandled database constraint violations to HTTP 409 JSON responses.

    Args:
        request: Incoming Starlette request.
        exc: Raised SQLAlchemy IntegrityError (e.g. a unique or foreign key violation).

    Returns:
        JSONResponse with status 409 and a generic conflict message as detail.
    """
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=
        {
            "detail": "The request conflicts with existing data",
        },
    )