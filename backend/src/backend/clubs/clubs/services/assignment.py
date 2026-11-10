from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.clubs.clubs.exceptions.club import InvalidPlatformManagerError
from src.backend.clubs.clubs.models.club import Club
from src.backend.clubs.clubs.repository.club import ClubRepository
from src.backend.identity.auth.models.auth import User
from src.backend.identity.auth.schemas.auth import UserRoleEnum

# Key for the transaction-scoped Postgres advisory lock that serializes assignments,
# so two clubs created at the same moment can't both pick the same "least loaded" moderator.
_ASSIGNMENT_LOCK_KEY = 0x434C5542  # "CLUB"


class ClubAssignmentService:
    """Distributes clubs evenly across platform moderators ("platform managers").

    Each club is overseen by one platform moderator. A new (or orphaned)
    club goes to the eligible moderator with the fewest non-archived clubs, ties broken by
    lowest user ID. An unarchived club returns to its previous moderator
    while they're still eligible. Existing assignments are never moved to rebalance, so a newly appointed
    moderator catches up by receiving every new club until the counts are level.

    Methods only flush; the caller owns the transaction and commits.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.club_repo = ClubRepository(session)

    async def _lock(self) -> None:
        """Takes the assignment advisory lock until the current transaction ends."""
        await self.session.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": _ASSIGNMENT_LOCK_KEY})

    async def _get_loads(self, exclude_id: int | None = None) -> dict[int, int]:
        """Returns {manager_id: active_club_count} for eligible moderators.

        Args:
            exclude_id: Moderator to leave out (e.g. one being demoted or deleted).
        """
        rows = await self.club_repo.get_platform_manager_loads()
        return {manager_id: count for manager_id, _, count in rows if manager_id != exclude_id}

    @staticmethod
    def _pick(loads: dict[int, int]) -> int | None:
        """Returns the least-loaded moderator ID (lowest ID on ties), or None if there are none."""
        if not loads:
            return None
        return min(loads, key=lambda manager_id: (loads[manager_id], manager_id))

    async def _distribute(self, clubs: list[Club], exclude_id: int | None = None) -> int:
        """Assigns each club in turn to the currently least-loaded moderator.

        Returns:
            Number of clubs that received a moderator.
        """
        loads = await self._get_loads(exclude_id)
        assigned = 0
        for club in clubs:
            manager_id = self._pick(loads)
            await self.club_repo.set_platform_manager(club, manager_id)
            if manager_id is not None:
                loads[manager_id] += 1
                assigned += 1
        return assigned

    async def assign(self, club: Club) -> int | None:
        """Assigns a club to the least-loaded platform moderator.

        If no eligible moderator exists the club is left unassigned; it is picked up
        later by `assign_unassigned` (run automatically when a moderator is appointed
        or reactivated, or manually by an admin).

        Args:
            club: Club to assign.

        Returns:
            ID of the assigned moderator, or None if the club was left unassigned.
        """
        await self._lock()
        # Clear any previous link first so the club doesn't count toward its old moderator's
        # load while picking (matters on unarchive, where the club is already active again).
        await self.club_repo.set_platform_manager(club, None)
        await self._distribute([club])
        return club.platform_manager_id

    async def restore(self, club: Club) -> int | None:
        """Re-attaches an unarchived club to its previous platform moderator, if still eligible.

        The club keeps its moderator link while archived. If that moderator is still an
        active, non-deleted platform moderator, the club simply stays with them. Otherwise
        (demoted, deactivated, deleted, or never assigned) it is assigned by the usual
        least-loaded rule.

        Args:
            club: Club that was just unarchived.

        Returns:
            ID of the moderator the club now belongs to, or None if it was left unassigned.
        """
        if club.platform_manager_id is not None:
            previous = await self.session.get(User, club.platform_manager_id)
            if previous and previous.role == UserRoleEnum.moderator and previous.is_active and not previous.is_deleted:
                return previous.id
        return await self.assign(club)

    async def reassign_all_from(self, manager: User) -> int:
        """Moves every non-archived club of a moderator to the remaining moderators.

        Used when a moderator is demoted, deactivated, or deleted. Clubs are handed out one
        at a time to whoever is least loaded, so they spread evenly. Archived clubs keep
        their link (they don't count toward anyone's load; on unarchive `restore` sees the moderator is
        no longer eligible and assigns them by the least-loaded rule).

        Args:
            manager: Moderator losing their clubs.

        Returns:
            Number of clubs that received a new moderator.
        """
        await self._lock()
        clubs = await self.club_repo.get_active_clubs_by_manager(manager.id)
        return await self._distribute(clubs, exclude_id=manager.id)

    async def assign_unassigned(self) -> int:
        """Assigns every non-archived club that has no moderator.

        Returns:
            Number of clubs that received a moderator.
        """
        await self._lock()
        clubs = await self.club_repo.get_unassigned_active_clubs()
        return await self._distribute(clubs)

    async def set_manager(self, club: Club, manager: User) -> None:
        """Manually assigns a club to a specific platform moderator.

        The club then counts toward that moderator's load like any other.

        Args:
            club: Club to assign.
            manager: Platform moderator to assign it to.

        Raises:
            InvalidPlatformManagerError: When the user is not an active platform moderator.
        """
        if manager.role != UserRoleEnum.moderator or not manager.is_active or manager.is_deleted:
            raise InvalidPlatformManagerError("User is not an active platform moderator")
        await self._lock()
        await self.club_repo.set_platform_manager(club, manager.id)
