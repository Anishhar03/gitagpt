import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.gzip import GZipMiddleware

from .config import settings
from .logging_config import configure_logging
from .metrics import HTTP_LATENCY, HTTP_REQUESTS
from .routers import auth, conversations, health, knowledge
from .seed import enqueue_default_document


configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        enqueue_default_document()
    except Exception:
        logger.exception("default_document_seed_failed")
    yield


app = FastAPI(
    title="Gita GPT Platform API",
    version="2.0.0",
    description="Scalable, source-grounded Bhagavad Gita conversation platform.",
    lifespan=lifespan,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    started = time.perf_counter()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    try:
        response = await call_next(request)
    finally:
        structlog.contextvars.clear_contextvars()
    duration = time.perf_counter() - started
    path = request.url.path
    HTTP_REQUESTS.labels(request.method, path, response.status_code).inc()
    HTTP_LATENCY.labels(request.method, path).observe(duration)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(health.router)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(conversations.router, prefix=settings.api_prefix)
app.include_router(knowledge.router, prefix=settings.api_prefix)


@app.get("/assets/krishna", include_in_schema=False)
def krishna_image():
    path = Path(settings.background_image_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Background image is not configured")
    return FileResponse(path, media_type="image/jpeg")
