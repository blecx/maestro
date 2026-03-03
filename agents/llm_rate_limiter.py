"""llm_rate_limiter.py - Async request throttle and rate-limited HTTP client.

Extracted from llm_client.py to satisfy SRP: rate-limiting concerns
are isolated here; LLMClientFactory in llm_client.py composes them.
"""

import asyncio
import random
import time
from typing import Awaitable, Callable, Optional

import httpx


class LLMRequestThrottle:
    """Process-local async request throttle for outbound LLM calls."""

    def __init__(
        self,
        *,
        max_rps: float,
        jitter_ratio: float,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], Awaitable[None]] = asyncio.sleep,
        jitter_fn: Callable[[float, float], float] = random.uniform,
    ):
        self.max_rps = max_rps
        self.min_interval = 1.0 / max_rps
        self.jitter_ratio = jitter_ratio
        self._clock = clock
        self._sleeper = sleeper
        self._jitter_fn = jitter_fn
        self._lock = asyncio.Lock()
        self._last_request_time: Optional[float] = None

    async def acquire(self) -> None:
        """Wait until the next request slot is available."""
        async with self._lock:
            now = self._clock()
            if self._last_request_time is None:
                self._last_request_time = now
                return

            elapsed = now - self._last_request_time
            remaining = max(0.0, self.min_interval - elapsed)
            jitter_cap = self.min_interval * self.jitter_ratio
            jitter = self._jitter_fn(0.0, jitter_cap) if jitter_cap > 0 else 0.0
            wait_seconds = remaining + jitter

            if wait_seconds > 0:
                await self._sleeper(wait_seconds)
                now = self._clock()

            self._last_request_time = now


class RateLimitedAsyncHTTPClient(httpx.AsyncClient):
    """httpx client wrapper that throttles before each outbound request."""

    def __init__(self, *, throttle: LLMRequestThrottle):
        super().__init__()
        self._throttle = throttle

    async def send(self, request, **kwargs):
        await self._throttle.acquire()
        return await super().send(request, **kwargs)


# Legacy private aliases kept for backwards-compat with llm_client.py internals
_LLMRequestThrottle = LLMRequestThrottle
_RateLimitedAsyncHTTPClient = RateLimitedAsyncHTTPClient
