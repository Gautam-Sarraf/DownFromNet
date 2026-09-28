import time
from collections import defaultdict
from fastapi import Request
from app.core.config import settings
from app.core.errors import RateLimitExceededError


class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter per IP address.
    """
    def __init__(self):
        self.requests = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> tuple[bool, int]:
        now = time.time()
        timestamps = self.requests[key]

        # Prune older than window
        cutoff = now - window_seconds
        valid_timestamps = [t for t in timestamps if t > cutoff]
        self.requests[key] = valid_timestamps

        if len(valid_timestamps) >= max_requests:
            retry_after = int(window_seconds - (now - valid_timestamps[0])) + 1
            return False, max(1, retry_after)

        self.requests[key].append(now)
        return True, 0

    def check_limit(self, request: Request, endpoint_type: str = "analyze"):
        # Extract client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        if endpoint_type == "analyze":
            limit = settings.RATE_LIMIT_ANALYZE_PER_MINUTE
        else:
            limit = settings.RATE_LIMIT_DOWNLOAD_PER_MINUTE

        key = f"{endpoint_type}:{client_ip}"
        allowed, retry_after = self.is_allowed(key, max_requests=limit, window_seconds=60)
        if not allowed:
            raise RateLimitExceededError(
                f"Rate limit exceeded for {endpoint_type}. Please try again in {retry_after} seconds."
            )


rate_limiter = InMemoryRateLimiter()
