from src.backend.identity.auth.models import User
from src.backend.library.shelf.exceptions import IsNotShelfOwnerError
from src.backend.library.shelf.models import Shelf


async def is_shelf_owner(
        user: User,
        shelf: Shelf,
) -> None:
    """Verifies that the given user owns the given shelf.

    Args:
        user: User to check.
        shelf: Shelf to check ownership of.

    Raises:
        IsNotShelfOwnerError: When the user does not own the shelf.
    """
    if shelf.user_id != user.id:
        raise IsNotShelfOwnerError("Only shelf owner can change their list")
    return