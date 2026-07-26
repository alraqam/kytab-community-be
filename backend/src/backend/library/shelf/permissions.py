from src.backend.identity.auth.models import User
from src.backend.library.shelf.exceptions import IsNotShelfOwnerError
from src.backend.library.shelf.models import Shelf


async def is_shelf_owner(
        user: User,
        shelf: Shelf,
) -> None:
    if shelf.user_id != user.id:
        raise IsNotShelfOwnerError("Only shelf owner can change their list")
    return