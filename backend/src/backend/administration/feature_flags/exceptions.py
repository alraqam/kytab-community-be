from src.backend.core.exceptions import NotFound


class FeatureFlagNotFoundError(NotFound):
    """Raised when the requested feature flag does not exist."""
