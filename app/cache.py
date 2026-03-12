"""Cache in-memory."""

import time
from typing import Optional

_cache: dict[str, tuple[dict, float]] = {}
TTL_SECONDS = 3600


async def get_cached(key: str) -> Optional[dict]:
    """Obtem valor do cache."""
    if key in _cache:
        val, expiry = _cache[key]
        if time.time() < expiry:
            return val
        del _cache[key]
    return None


async def set_cached(key: str, value: dict, ttl: int = TTL_SECONDS):
    """Armazena no cache."""
    _cache[key] = (value, time.time() + ttl)
