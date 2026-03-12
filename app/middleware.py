"""Middlewares."""

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import RATE_LIMIT

_rate_store: dict[str, list[float]] = defaultdict(list)
WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limita requisicoes por IP."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/static") or request.url.path in ("/health", "/sw.js"):
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.time()
        _rate_store[ip] = [t for t in _rate_store[ip] if now - t < WINDOW]

        if len(_rate_store[ip]) >= RATE_LIMIT:
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )

        _rate_store[ip].append(now)
        return await call_next(request)
