from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """Checks whether a string is a valid HTTP or HTTPS URL.

    Args:
        url: URL string to validate.

    Returns:
        True if the URL has a valid scheme (http/https) and netloc; False otherwise.
    """
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False