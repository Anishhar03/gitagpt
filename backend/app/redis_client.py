from functools import lru_cache

from redis import Redis
from rq import Queue

from .config import settings


@lru_cache(maxsize=1)
def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=False)


def get_queue() -> Queue:
    return Queue("ingestion", connection=get_redis(), default_timeout=900)
