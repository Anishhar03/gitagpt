from uuid import UUID

import structlog
from pypdf import PdfReader
from sqlalchemy import delete
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Chunk, Document
from .embeddings import get_embedding_service


logger = structlog.get_logger(__name__)


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []
    chunks = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        if end < len(normalized):
            boundary = normalized.rfind(". ", start + chunk_size // 2, end)
            if boundary > start:
                end = boundary + 1
        chunks.append(normalized[start:end].strip())
        if end >= len(normalized):
            break
        start = max(start + 1, end - overlap)
    return chunks


def ingest_document(db: Session, document_id: UUID) -> None:
    document = db.get(Document, document_id)
    if document is None:
        raise ValueError("document no longer exists")
    document.status = "processing"
    document.error_message = None
    db.commit()

    try:
        reader = PdfReader(document.storage_path)
        records = []
        ordinal = 0
        for page_index, page in enumerate(reader.pages, start=1):
            for text in split_text(page.extract_text() or "", settings.chunk_size, settings.chunk_overlap):
                records.append((ordinal, page_index, text))
                ordinal += 1

        if not records:
            raise ValueError("PDF contains no extractable text")

        db.execute(delete(Chunk).where(Chunk.document_id == document.id))
        embeddings = get_embedding_service().embed_many([record[2] for record in records])
        for (ordinal, page_number, text), embedding in zip(records, embeddings, strict=True):
            db.add(
                Chunk(
                    document_id=document.id,
                    ordinal=ordinal,
                    page_number=page_number,
                    content=text,
                    token_count=max(1, len(text.split())),
                    embedding=embedding,
                    source_metadata={"filename": document.filename},
                )
            )
        document.status = "ready"
        document.chunk_count = len(records)
        db.commit()
        logger.info("document_ingested", document_id=str(document.id), chunks=len(records))
    except Exception as exc:
        db.rollback()
        document = db.get(Document, document_id)
        if document is not None:
            document.status = "failed"
            document.error_message = f"{type(exc).__name__}: {str(exc)[:500]}"
            db.commit()
        logger.exception("document_ingestion_failed", document_id=str(document_id))
        raise
