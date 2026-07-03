from fastapi import HTTPException

from ..config import settings
from ..redis_client import get_redis


def enforce_rate_limit(subject: str) -> None:
    key = f"rate:chat:{subject}"
    redis = get_redis()
    with redis.pipeline() as pipeline:
        pipeline.incr(key)
        pipeline.expire(key, 60, nx=True)
        count, _ = pipeline.execute()
    if int(count) > settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Chat rate limit exceeded. Try again shortly.")
