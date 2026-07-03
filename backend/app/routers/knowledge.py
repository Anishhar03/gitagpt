from datetime import date
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import Bookmark, Chunk, Document, User
from ..redis_client import get_queue, get_redis
from ..schemas import BookmarkCreate, BookmarkOut, DailyWisdomOut, DocumentOut, SourceOut
from ..security import get_current_user, require_admin
from ..services.storage import persist_upload


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def source_from_chunk(chunk: Chunk, document: Document, score: float = 1.0) -> SourceOut:
    return SourceOut(
        chunk_id=chunk.id,
        document_id=document.id,
        title=document.title,
        translation=document.translation,
        page_number=chunk.page_number,
        excerpt=chunk.content[:1200],
        score=score,
    )


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(select(Document).order_by(Document.created_at.desc())).all()


@router.post("/documents", response_model=DocumentOut, status_code=202)
def upload_document(
    title: str = Form(min_length=2, max_length=200),
    translation: str = Form(default="Unknown", max_length=120),
    file: UploadFile = File(),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF documents are supported")
    content = file.file.read(settings.max_upload_bytes + 1)
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="PDF exceeds the configured upload limit")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF")
    path, checksum = persist_upload(file.filename, content)
    existing = db.scalar(select(Document).where(Document.checksum == checksum))
    if existing is not None:
        path.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail="This document has already been uploaded")
    document = Document(
        title=title.strip(),
        translation=translation.strip() or "Unknown",
        filename=file.filename,
        storage_path=str(path),
        checksum=checksum,
        status="queued",
        uploaded_by_id=admin.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    get_queue().enqueue("app.tasks.ingest_document_job", str(document.id), job_timeout=900)
    return document


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: UUID,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(document.storage_path)
    db.delete(document)
    path.unlink(missing_ok=True)
    return Response(status_code=204)


@router.get("/daily", response_model=DailyWisdomOut)
def daily_wisdom(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cache_key = f"daily:{date.today().isoformat()}"
    cached = get_redis().get(cache_key)
    if cached:
        return DailyWisdomOut.model_validate_json(cached)

    count = db.scalar(select(func.count()).select_from(Chunk).join(Document).where(Document.status == "ready")) or 0
    if count == 0:
        raise HTTPException(status_code=503, detail="The knowledge base is still being prepared")
    offset = int(date.today().strftime("%Y%m%d")) % count
    row = db.execute(
        select(Chunk, Document)
        .join(Document)
        .where(Document.status == "ready")
        .order_by(Chunk.id)
        .offset(offset)
        .limit(1)
    ).one()
    source = source_from_chunk(row[0], row[1])
    result = DailyWisdomOut(
        source=source,
        reflection="Carry one line from this passage into a concrete action today, without attaching your peace to the result.",
    )
    get_redis().setex(cache_key, 86400, result.model_dump_json())
    return result


@router.get("/bookmarks", response_model=list[BookmarkOut])
def list_bookmarks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(Bookmark, Chunk, Document)
        .join(Chunk, Bookmark.chunk_id == Chunk.id)
        .join(Document, Chunk.document_id == Document.id)
        .where(Bookmark.user_id == user.id)
        .order_by(Bookmark.created_at.desc())
    ).all()
    return [
        BookmarkOut(
            id=bookmark.id,
            chunk_id=bookmark.chunk_id,
            note=bookmark.note,
            created_at=bookmark.created_at,
            source=source_from_chunk(chunk, document),
        )
        for bookmark, chunk, document in rows
    ]


@router.post("/bookmarks", response_model=BookmarkOut, status_code=201)
def create_bookmark(
    payload: BookmarkCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.execute(
        select(Chunk, Document).join(Document).where(Chunk.id == payload.chunk_id)
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Source passage not found")
    existing = db.scalar(
        select(Bookmark).where(Bookmark.user_id == user.id, Bookmark.chunk_id == payload.chunk_id)
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Source passage is already bookmarked")
    bookmark = Bookmark(user_id=user.id, chunk_id=payload.chunk_id, note=payload.note)
    db.add(bookmark)
    db.flush()
    return BookmarkOut(
        id=bookmark.id,
        chunk_id=bookmark.chunk_id,
        note=bookmark.note,
        created_at=bookmark.created_at,
        source=source_from_chunk(row[0], row[1]),
    )


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.scalar(
        select(Bookmark).where(Bookmark.id == bookmark_id, Bookmark.user_id == user.id)
    )
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    return Response(status_code=204)
