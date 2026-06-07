"""
Retry utilities for external API calls.

Provides exponential-backoff retry logic for transient network errors
(timeouts, connection resets, 5xx responses) from yfinance and mfapi.in.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

import httpx

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Errors that are safe to retry (transient network / server issues)
_RETRYABLE_EXCEPTIONS = (
    httpx.TimeoutException,       # read / connect / pool timeout
    httpx.ConnectError,           # DNS or TCP connection failed
    httpx.RemoteProtocolError,    # server closed connection mid-response
    asyncio.TimeoutError,         # asyncio-level timeout
    ConnectionResetError,
    TimeoutError,
)


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    retries: int = 3,
    base_delay: float = 2.0,
    backoff: float = 2.0,
    label: str = "",
) -> T:
    """
    Call an async function with exponential-backoff retries on transient errors.

    Args:
        fn:         Zero-argument async callable to call.
        retries:    Maximum number of additional attempts after the first failure.
        base_delay: Seconds to wait before the first retry.
        backoff:    Multiplier applied to delay after each failure.
        label:      Human-readable name for log messages (e.g. scheme code).

    Returns:
        The return value of ``fn`` on success.

    Raises:
        The last exception if all attempts fail.
    """
    delay = base_delay
    last_exc: Exception | None = None

    for attempt in range(1, retries + 2):  # +2 → first try + N retries
        try:
            return await fn()
        except _RETRYABLE_EXCEPTIONS as exc:
            last_exc = exc
            if attempt <= retries:
                logger.warning(
                    "Transient error%s (attempt %d/%d), retrying in %.1fs: %s",
                    f" [{label}]" if label else "",
                    attempt,
                    retries + 1,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
                delay *= backoff
            else:
                logger.error(
                    "All %d attempts failed%s: %s",
                    retries + 1,
                    f" [{label}]" if label else "",
                    exc,
                )

    raise last_exc  # type: ignore[misc]
