import os
from pathlib import Path

import pytest


TEST_ROOT = Path(__file__).parent
TEST_DATABASE = TEST_ROOT / "gitagpt-test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"
os.environ["REDIS_URL"] = "redis://unused:6379/0"
os.environ["SEED_DEFAULT_DOCUMENT"] = "false"
os.environ["AUTH_MODE"] = "development"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-local-tests"
os.environ["GOOGLE_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""
os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.routers import health, knowledge  # noqa: E402
from app.services import rate_limit  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.key = ""

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def incr(self, key):
        self.key = key
        return self

    def expire(self, *_args, **_kwargs):
        return self

    def execute(self):
        value = int(self.redis.values.get(self.key, 0)) + 1
        self.redis.values[self.key] = value
        return [value, True]


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def setex(self, key, _ttl, value):
        self.values[key] = value

    def pipeline(self):
        return FakePipeline(self)

    def ping(self):
        return True


@pytest.fixture(autouse=True)
def isolated_services(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    fake_redis = FakeRedis()
    monkeypatch.setattr(rate_limit, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(knowledge, "get_redis", lambda: fake_redis)
    monkeypatch.setattr(health, "get_redis", lambda: fake_redis)
    yield fake_redis
    Base.metadata.drop_all(engine)
    engine.dispose()
    TEST_DATABASE.unlink(missing_ok=True)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
