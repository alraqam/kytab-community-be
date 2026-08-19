from src.backend.core.exceptions import TooManyRequests
from src.backend.core.redis import redis_client

MAX_ATTEMPTS = 5
FAILURE_WINDOW_SECONDS = 900
BASE_LOCKOUT_SECONDS = 30
MAX_LOCKOUT_SECONDS = 900


class RateLimiter:
    """Tracks failed attempts per identifier in Redis and applies a progressive lockout."""

    def __init__(self, scope: str):
        self.scope = scope

    def _key(self, identifier: str) -> str:
        return f"ratelimit:{self.scope}:{identifier}"

    async def check(self, identifier: str) -> None:
        """Raises TooManyRequests if the identifier is currently locked out.

        Args:
            identifier: Key identifying the client (e.g. IP address, optionally with username).

        Raises:
            TooManyRequests: When the failure count has crossed MAX_ATTEMPTS and the lockout is active.
        """
        key = self._key(identifier)
        attempts = await redis_client.get(key)
        if attempts and int(attempts) >= MAX_ATTEMPTS:
            ttl = await redis_client.ttl(key)
            if ttl > 0:
                raise TooManyRequests(f"Too many failed attempts. Try again in {ttl} seconds.")

    async def record_failure(self, identifier: str) -> None:
        """Increments the failure count and applies an escalating lockout once the threshold is hit.

        Args:
            identifier: Key identifying the client (e.g. IP address, optionally with username).
        """
        key = self._key(identifier)
        attempts = await redis_client.incr(key)
        if attempts < MAX_ATTEMPTS:
            await redis_client.expire(key, FAILURE_WINDOW_SECONDS)
        else:
            lockout = min(BASE_LOCKOUT_SECONDS * 2 ** (attempts - MAX_ATTEMPTS), MAX_LOCKOUT_SECONDS)
            await redis_client.expire(key, lockout)

    async def reset(self, identifier: str) -> None:
        """Clears the failure count after a successful attempt.

        Args:
            identifier: Key identifying the client (e.g. IP address, optionally with username).
        """
        await redis_client.delete(self._key(identifier))
