from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.exceptions import NotClubMemberError
from src.backend.clubs.club_membership.repository.membership import ClubMembershipRepository
from src.backend.clubs.club_membership.schemas import MemberRole
from src.backend.clubs.club_membership.services import is_owner_or_moderator, is_club_owner
from src.backend.clubs.clubs.exceptions import InvalidCoverUrlError, ClubNotFoundError
from src.backend.clubs.clubs.models import Club
from src.backend.clubs.clubs.repository import ClubRepository
from src.backend.clubs.clubs.schemas import CreateClub, UpdateClub, ManageClubModerators
from src.backend.core.services import validate_image_upload
from src.backend.core.storage import StorageService
from src.backend.identity.auth.models import User
from src.backend.identity.users.exceptions import UserNotFoundError
from src.backend.identity.users.repository import UserRepository


class ClubManager:
    """Handles club business logic: creation, updates, archiving, and ownership transfer."""

    def __init__(
            self,
            session: AsyncSession,
            storage: StorageService,
    ):
        self.session = session
        self.storage = storage
        self.club_repo = ClubRepository(session)
        self.user_repo = UserRepository(session)
        self.membership_repo = ClubMembershipRepository(session)

    async def create_club(
            self,
            user: User,
            request: CreateClub,
    ) -> Club:
        """Creates a new club and registers the creating user as its owner.

        Args:
            user: User creating the club.
            request: CreateClub payload with name and description.

        Returns:
            Newly created Club instance.
        """
        result = await self.club_repo.create_club(
            name=request.name,
            description=request.description,
            user_id=user.id
        )
        await self.membership_repo.create_membership(result.id, user.id, MemberRole.club_owner)
        await self.session.commit()
        return await self.club_repo.get_club_by_id(result.id)

    async def update_club(
            self,
            user: User,
            club: Club,
            request: UpdateClub,
    ) -> None:
        """Updates a club's details after verifying the user is an owner or moderator.

        Args:
            user: User requesting the update.
            club: Club instance to update.
            request: UpdateClub payload with the fields to change.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator of the club.
        """
        is_owner_or_moderator(club, user.id)

        await self.club_repo.update_club(
            club=club,
            name=request.name,
            description=request.description,
            club_type=request.club_type,
            member_cap=request.member_cap,
        )
        await self.session.commit()

    async def update_cover(
            self,
            user: User,
            club: Club,
            file: UploadFile,
    ) -> None:
        """Uploads a new cover image and replaces the club's stored cover.

        Args:
            user: User requesting the update.
            club: Club instance to update.
            file: Uploaded cover image.

        Raises:
            IsNotClubOwnerError: When the user is not an owner or moderator of the club.
            InvalidCoverUrlError: When the image has an unsupported type or exceeds the size limit.
        """
        is_owner_or_moderator(club, user.id)

        content, extension = await validate_image_upload(file, InvalidCoverUrlError)

        old_cover = club.cover
        key = f"club-covers/{club.id}/{uuid4().hex}{extension}"
        await self.storage.upload(key, content, file.content_type)

        await self.club_repo.update_club(
            club=club,
            cover=key
        )
        await self.session.commit()

        if old_cover:
            await self.storage.delete(old_cover)

    async def archive_club(
            self,
            club: Club,
            user: User | None = None,
    ) -> None:
        """Archives a club, optionally restricting the action to the club's owner.

        Args:
            club: Club instance to archive.
            user: User requesting the archive, or None to skip the ownership check.

        Raises:
            IsNotClubOwnerError: When a user is given and is not the club's owner.
        """
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
        """Restores a previously archived club.

        Args:
            club: Club instance to unarchive.
        """
        await self.club_repo.update_status(
            club=club,
            status=False
        )
        await self.session.commit()

    async def get_clubs_list(
            self,
            filters,
    ) -> list[Club]:
        """Lists non-secret, non-archived clubs matching the given filters.

        Args:
            filters: ClubPublicFilter with search and ordering criteria.

        Returns:
            List of matching Club instances.
        """
        result = await self.club_repo.get_clubs_list(filters)
        return result

    async def get_all_clubs(
            self,
            filters
    ) -> list[Club]:
        """Lists all clubs matching the given filters, including secret and archived ones.

        Args:
            filters: ClubFilter with search and ordering criteria.

        Returns:
            List of matching Club instances.
        """
        result = await self.club_repo.get_all_clubs(filters)
        return result

    async def get_club_by_id(
            self,
            club_id: int
    ) -> Club:
        """Fetches a single club by ID.

        Args:
            club_id: ID of the club to fetch.

        Returns:
            Matching Club instance.

        Raises:
            ClubNotFoundError: When no club matches the ID.
        """
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
        """Transfers club ownership from the current owner to another member.

        Args:
            club: Club instance whose ownership is being transferred.
            user: Current owner of the club requesting the transfer.
            request: ManageClubModerators payload with the new owner's user ID.

        Raises:
            IsNotClubOwnerError: When the requesting user is not the club's owner.
            UserNotFoundError: When no user matches the given user ID.
            NotClubMemberError: When the current owner or the new owner has no membership in the club.
        """
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
