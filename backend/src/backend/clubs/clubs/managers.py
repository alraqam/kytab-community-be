from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.exceptions import NotClubMemberError
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.schemas import MemberRole
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_owner
from src.backend.clubs.clubs.exceptions import InvalidCoverUrlError, ClubNotFoundError
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.repository import ClubRepository
from src.backend.clubs.clubs.schemas import CreateClub, UpdateClub, ManageClubModerators
from src.backend.core.services import is_valid_url
from src.backend.identity.auth.models import User
from src.backend.identity.users.exceptions import UserNotFoundError
from src.backend.identity.users.repository import UserRepository


class ClubManager:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.club_repo = ClubRepository(session)
        self.user_repo = UserRepository(session)
        self.membership_repo = ClubMembershipRepository(session)

    async def create_club(
            self,
            user: User,
            request: CreateClub,
    ) -> Club:
        result = await self.club_repo.create_club(
            name=request.name,
            description=request.description,
            user_id=user.id
        )
        await self.membership_repo.create_membership(result.id, user.id, MemberRole.club_owner)
        await self.session.commit()
        return result

    async def update_club(
            self,
            user: User,
            club: Club,
            request: UpdateClub,
    ) -> None:
        is_owner_or_moderator(club, user.id)
        if request.cover is not None and not is_valid_url(request.cover):
                raise InvalidCoverUrlError("Invalid cover url format")

        await self.club_repo.update_club(
            club=club,
            name=request.name,
            description=request.description,
            club_type=request.club_type,
            cover=request.cover
        )
        await self.session.commit()

    async def archive_club(
            self,
            club: Club,
            user: User | None = None,
    ) -> None:
        if user:
            is_club_owner(club, user)
        await self.club_repo.update_status(
            club=club,
            status=True
        )
        await self.session.commit()

    async def unarchive_club(
            self,
            club: Club,
    ) -> None:
        await self.club_repo.update_status(
            club=club,
            status=False
        )
        await self.session.commit()

    async def get_clubs_list(
            self,
            filters,
    ) -> list[Club]:
        result = await self.club_repo.get_clubs_list(filters)
        return result

    async def get_all_clubs(
            self,
            filters
    ) -> list[Club]:
        result = await self.club_repo.get_all_clubs(filters)
        return result

    async def get_club_by_id(
            self,
            club_id: int
    ) -> Club:
        result = await self.club_repo.get_club_by_id(
            club_id=club_id
        )
        if not result:
            raise ClubNotFoundError("Club not found")
        return result


    async def transfer_ownership(
            self,
            club: Club,
            user: User,
            request: ManageClubModerators
    ) -> None:
        is_club_owner(club, user)
        new_owner = await self.user_repo.get_user_by_id(request.user_id)
        if not new_owner:
            raise UserNotFoundError("User not found")

        await self.club_repo.transfer_ownership(club, new_owner.id)

        membership = await self.membership_repo.get_user_club_membership(club, user)
        if not membership:
            raise NotClubMemberError("Membership not found")
        await self.membership_repo.change_member_role(membership, MemberRole.member)

        membership = await self.membership_repo.get_user_club_membership(club, new_owner)
        if not membership:
            raise NotClubMemberError("Membership not found")
        await self.membership_repo.change_member_role(membership, MemberRole.club_owner)

        await self.session.commit()
