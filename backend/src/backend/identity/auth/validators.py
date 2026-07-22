import re

from src.backend.identity.auth.exceptions import WeakPasswordError


def validate_password(value):
    """Validates that a password meets strength requirements (length, case, digit, special char).

    Args:
        value: Plain-text password string to validate.

    Returns:
        The original password string if valid.

    Raises:
        WeakPasswordError: When any strength requirement is not met.
    """
    if len(value) < 8:
        raise WeakPasswordError("The password must contain at least 8 characters")
    if not re.search(r"[A-ZА-Я]", value):
        raise WeakPasswordError("The password must contain at least one uppercase letter")
    if not re.search(r"[a-zа-я]", value):
        raise WeakPasswordError("The password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", value):
        raise WeakPasswordError("The password must contain at least one digit")
    if not re.search(r"[\W_]", value):
        raise WeakPasswordError("The password must contain at least one special character")
    return value