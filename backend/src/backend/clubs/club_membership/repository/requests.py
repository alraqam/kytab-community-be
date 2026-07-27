from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.club_membership.models import ClubJoinRequest
from src.backend.clubs.club_membership.schemas import JoinRequestStatus


@dataclass
class ClubJoinRequestRepository:
    """Data access layer for ClubJoinRequest model operations."""

    session: AsyncSession

    async def create_request(
            self,
            club_id: int,
            user_id: int,
    ) -> ClubJoinRequest:
        """Creates a new join request with a 7-day expiry.

        Args:
            club_id: ID of the club the user wants to join.
            user_id: ID of the user sending the request.

        Returns:
            Newly created ClubJoinRequest instance.
        """
        result = ClubJoinRequest(
            club_id=club_id,
            user_id=user_id,
            expires_at=datetime.now() + timedelta(days=7)
        )
        self.session.add(result)
        await self.session.flush()
        return result

    async def update_request_status(
            self,
            request: ClubJoinRequest,
            status: str
    ) -> None:
        """Updates the status of a join request and flushes the session.

        Args:
            request: ClubJoinRequest instance to update.
            status: New status string.
        """
        request.status = status
        self.session.add(request)
        await self.session.flush()

    async def get_request_by_id(
            self,
            request_id: int,
    ) -> ClubJoinRequest | None:
        """Fetches a join request by its ID.

        Args:
            request_id: ID of the join request.

        Returns:
            ClubJoinRequest instance if found, None otherwise.
        """
        stmt = select(ClubJoinRequest).where(ClubJoinRequest.id == request_id)
        result = await self.session.execute(stmt)
        request = result.scalar_one_or_none()
        return request

    async def get_club_requests(
            self,
            club_id: int
    ) -> list[ClubJoinRequest]:
        """Returns all pending, non-expired join requests for a club.

        Args:
            club_id: ID of the club.

        Returns:
            List of pending ClubJoinRequest instances.
        """
        stmt = select(ClubJoinRequest).where(
            and_(
                ClubJoinRequest.club_id == club_id,
                ClubJoinRequest.status == JoinRequestStatus.pending,
                ClubJoinRequest.expires_at >= datetime.now()
            ))
        result = await self.session.execute(stmt)
        request = result.scalars().all()
        return request