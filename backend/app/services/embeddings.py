import hashlib
import math
import re
from functools import lru_cache

import structlog

from ..config import settings


logger = structlog.get_logger(__name__)
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9']+")


def deterministic_embedding(text: str) -> list[float]:
    vector = [0.0] * settings.embedding_dimensions
    for token in TOKEN_PATTERN.findall(text.lower()):
        digest = hashlib.blake2b(token.encode(), digest_size=8).digest()
        index = int.from_bytes(digest[:4], "big") % settings.embedding_dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class EmbeddingService:
    def __init__(self):
        self.provider = "local"
        self._client = None
        if settings.google_api_key:
            try:
                from google import genai

                self._client = genai.Client(api_key=settings.google_api_key)
                self.provider = "gemini"
            except Exception:
                logger.exception("embedding_client_initialization_failed")

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if self._client is None:
            return [deterministic_embedding(text) for text in texts]
        try:
            from google.genai import types

            response = self._client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=texts,
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.embedding_dimensions,
                    task_type="RETRIEVAL_DOCUMENT",
                ),
            )
            return [list(item.values) for item in response.embeddings]
        except Exception:
            logger.exception("gemini_embedding_failed", count=len(texts))
            return [deterministic_embedding(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        if self._client is None:
            return deterministic_embedding(text)
        try:
            from google.genai import types

            response = self._client.models.embed_content(
                model=settings.gemini_embedding_model,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=settings.embedding_dimensions,
                    task_type="RETRIEVAL_QUERY",
                ),
            )
            return list(response.embeddings[0].values)
        except Exception:
            logger.exception("gemini_query_embedding_failed")
            return deterministic_embedding(text)


@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
