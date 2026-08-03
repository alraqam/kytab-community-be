from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.blocked_users.exceptions import UserAlreadyBlockedError, NotBlockOwnerError, \
    BlockNotFoundError
from src.backend.identity.blocked_users.models import BlockedUser
from src.backend.identity.blocked_users.repository import BlockedUsersRepository
from src.backend.identity.blocked_users.schemas import CreateBlock


class BlockedUserManager:
    """Handles blocked-user business logic: blocking, unblocking, and lookups."""

    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.blocked_users_repo = BlockedUsersRepository(session)


    async def block_user(
            self,
            user: User,
            request: CreateBlock,
    ) -> BlockedUser:
        """Creates a block from the given user against the target user.

        Args:
            user: User creating the block.
            request: CreateBlock payload with the ID of the user to block.

        Returns:
            Newly created BlockedUser instance.

        Raises:
            UserAlreadyBlockedError: When the user has already blocked the target.
        """
        try:
            result = await self.blocked_users_repo.block_user(
                blocker_id=user.id,
                blocked_id=request.blocked_id
            )
            await self.session.commit()
            return result
        except IntegrityError:
            raise UserAlreadyBlockedError("User already blocked")

    async def delete_block(
            self,
            user: User,
            block: BlockedUser
    ) -> None:
        """Deletes a block, ensuring only its owner can remove it.

        Args:
            user: User requesting the deletion.
            block: BlockedUser instance to delete.

        Raises:
            NotBlockOwnerError: When the requesting user is not the block's owner.
        """
        if user.id != block.blocker_id:
            raise NotBlockOwnerError("Only block owners can delete block")

        await self.blocked_users_repo.delete_block(
            block=block
        )
        await self.session.commit()

    async def get_user_blocked(
            self,
            user: User,
    ) -> list[BlockedUser]:
        """Lists all users blocked by the given user.

        Args:
            user: User whose blocks are being fetched.

        Returns:
            List of BlockedUser instances created by the user.
        """
        result = await self.blocked_users_repo.get_user_blocked(
            user_id=user.id,
        )
        return result

    async def get_block_by_id(
            self,
            block_id: int
    ) -> BlockedUser:
        """Fetches a single block by ID.

        Args:
            block_id: ID of the block to fetch.

        Returns:
            Matching BlockedUser instance.

        Raises:
            BlockNotFoundError: When no block matches the ID.
        """
        result = await self.blocked_users_repo.get_block_by_id(
            block_id=block_id,
        )
        if not result:
            raise BlockNotFoundError("Block not found")
        return result

    async def is_blocked_user(
            self,
            blocker_id: int,
            blocked_id: int
    ) -> bool:
        """Checks whether one user has blocked another.

        Args:
            blocker_id: ID of the user who may have created the block.
            blocked_id: ID of the potentially blocked user.

        Returns:
            True if a block exists between the two users, False otherwise.
        """
        result = await self.blocked_users_repo.is_blocked_user(
            blocker_id=blocker_id,
            blocked_id=blocked_id,
        )
        return True if result else False