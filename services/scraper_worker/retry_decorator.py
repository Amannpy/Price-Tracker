import asyncio
import logging
import random
from functools import wraps
from typing import Callable, Any, Coroutine

logger = logging.getLogger(__name__)


def retry_backoff(
    max_attempts: int = 3,
    base: float = 2.0,
    jitter: float = 0.3,
    retry_exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Callable[..., Coroutine[Any, Any, Any]]]:
    """
    Simple async retry decorator with exponential backoff and jitter.

    Usage:
        @retry_backoff(max_attempts=3, base=2.0)
        async def fetch(...):
            ...
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            last_exc: BaseException | None = None

            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except retry_exceptions as exc:
                    attempt += 1
                    last_exc = exc
                    if attempt >= max_attempts:
                        logger.error(f"{func.__name__} failed after {attempt} attempts: {exc}")
                        raise

                    sleep_for = base ** attempt
                    # apply jitter
                    sleep_for *= random.uniform(1 - jitter, 1 + jitter)
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {exc}. "
                        f"Retrying in {sleep_for:.2f}s..."
                    )
                    await asyncio.sleep(sleep_for)

            # Should not reach here
            if last_exc:
                raise last_exc

        return wrapper

    return decorator


