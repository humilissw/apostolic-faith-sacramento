"""Simple in-memory rate limiter for single-server deployments."""

import time
from collections import defaultdict

_requests: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """Check if the request is within the rate limit."""
    now = time.time()
    window_start = now - window_seconds
    _requests[key] = [t for t in _requests[key] if t > window_start]
    if len(_requests[key]) >= max_requests:
        return False
    _requests[key].append(now)
    return True


def reset_rate_limit() -> None:
    """Clear all rate limiter state."""
    _requests.clear()
