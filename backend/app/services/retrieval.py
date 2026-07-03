import math
import re
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..metrics import RETRIEVAL_LATENCY
from ..models import Chunk, Document
from .embeddings import get_embedding_service


WORD_PATTERN = re.compile(r"[A-Za-z0-9']+")


def cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(value * value for value in left)) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right)) or 1.0
    return numerator / (left_norm * right_norm)


def retrieve_sources(db: Session, query: str, top_k: int | None = None) -> list[dict]:
    started = time.perf_counter()
    top_k = top_k or settings.retrieval_top_k
    query_vector = get_embedding_service().embed_query(query)
    dialect = db.get_bind().dialect.name

    base = select(Chunk, Document).join(Document).where(Document.status == "ready")
    if dialect == "postgresql":
        distance = Chunk.embedding.cosine_distance(query_vector)
        rows = db.execute(base.order_by(distance).limit(max(top_k * 5, 20))).all()
    else:
        rows = db.execute(base.limit(2000)).all()

    query_terms = set(WORD_PATTERN.findall(query.lower()))
    ranked = []
    for chunk, document in rows:
        semantic = cosine_similarity(query_vector, list(chunk.embedding))
        chunk_terms = set(WORD_PATTERN.findall(chunk.content.lower()))
        lexical = len(query_terms & chunk_terms) / max(len(query_terms), 1)
        score = semantic * 0.78 + lexical * 0.22
        ranked.append((score, chunk, document))

    ranked.sort(key=lambda item: item[0], reverse=True)
    results = [
        {
            "chunk_id": chunk.id,
            "document_id": document.id,
            "title": document.title,
            "translation": document.translation,
            "page_number": chunk.page_number,
            "excerpt": chunk.content[:1200],
            "score": round(float(score), 5),
        }
        for score, chunk, document in ranked[:top_k]
    ]
    RETRIEVAL_LATENCY.observe(time.perf_counter() - started)
    return results
