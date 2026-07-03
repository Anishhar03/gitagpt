import shutil
from sqlalchemy import select

import structlog

from .config import settings
from .database import SessionLocal
from .models import Document
from .redis_client import get_queue
from .services.ingestion import ingest_document
from .services.storage import checksum_file


logger = structlog.get_logger(__name__)


def enqueue_default_document() -> None:
    source = settings.default_pdf_path
    if not settings.seed_default_document or not source.exists():
        return
    checksum = checksum_file(source)
    with SessionLocal() as db:
        existing = db.scalar(select(Document).where(Document.checksum == checksum))
        if existing is not None:
            return
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        target = settings.upload_dir / f"default-{checksum[:12]}.pdf"
        if not target.exists():
            shutil.copyfile(source, target)
        document = Document(
            title="Bhagavad Gita",
            translation="Bundled reference edition",
            filename=source.name,
            storage_path=str(target),
            checksum=checksum,
            status="queued",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        if settings.ingestion_mode == "inline":
            ingest_document(db, document.id)
            logger.info("default_document_ingested_inline", document_id=str(document.id))
        else:
            get_queue().enqueue("app.tasks.ingest_document_job", str(document.id), job_timeout=900)
            logger.info("default_document_enqueued", document_id=str(document.id))
