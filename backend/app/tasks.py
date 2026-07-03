from uuid import UUID

from .database import SessionLocal
from .services.ingestion import ingest_document


def ingest_document_job(document_id: str) -> None:
    with SessionLocal() as db:
        ingest_document(db, UUID(document_id))
