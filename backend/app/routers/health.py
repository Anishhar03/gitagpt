from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import text

from ..database import SessionLocal
from ..redis_client import get_redis


router = APIRouter(tags=["operations"])


@router.get("/health/live")
def liveness():
    return {"status": "ok"}


@router.get("/health/ready")
def readiness():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    get_redis().ping()
    return {"status": "ready", "dependencies": {"postgres": "up", "redis": "up"}}


@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
