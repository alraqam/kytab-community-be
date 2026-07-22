from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.identity.auth.models import User
from src.backend.identity.blocked_users.exceptions import UserAlreadyBlockedError, NotBlockOwnerError, \
    BlockNotFoundError
from src.backend.identity.blocked_users.models import BlockedUser
from src.backend.identity.blocked_users.repository import BlockedUsersRepository
from src.backend.identity.blocked_users.schemas import CreateBlock


class BlockedUserManager:
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
        result = await self.blocked_users_repo.get_user_blocked(
            user_id=user.id,
        )
        return result

    async def get_block_by_id(
            self,
            block_id: int
    ) -> BlockedUser:
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
        result = await self.blocked_users_repo.is_blocked_user(
            blocker_id=blocker_id,
            blocked_id=blocked_id,
        )
        print(result)
        return True if result else False