import asyncio
import random
import functools
import logging

logger = logging.getLogger(__name__)

def retry_backoff(max_attempts=5, base=1.0, cap=30.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"Max retries ({max_attempts}) exceeded for {func.__name__}")
                        raise
                    
                    sleep = min(cap, base * (2 ** (attempt - 1)))
                    jitter = sleep * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed: {str(e)[:100]}. Retrying in {jitter:.2f}s")
                    await asyncio.sleep(jitter)
        return wrapper
    return decorator
