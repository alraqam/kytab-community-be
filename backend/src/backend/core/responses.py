from src.backend.core.schemas import ErrorResponse

ERROR_DESCRIPTIONS = {
    400: "Bad request: the input is invalid",
    401: "Not authenticated, or the token is invalid or expired",
    403: "Permission denied",
    404: "Resource not found",
    409: "Conflict with the current state or existing data",
    429: "Too many requests; try again later",
    503: "An external service is unavailable",
}


def error_responses(*status_codes: int) -> dict[int | str, dict]:
    """Builds the OpenAPI `responses` mapping for the error statuses a route can return.

    Every error is returned by the exception handlers in core/handlers.py as
    `{"detail": "<message>"}`, so all codes share the ErrorResponse model.

    Args:
        status_codes: HTTP status codes the route can return on error.

    Returns:
        Mapping suitable for a route decorator's `responses` argument.
    """
    return {
        code: {"model": ErrorResponse, "description": ERROR_DESCRIPTIONS[code]}
        for code in status_codes
    }
