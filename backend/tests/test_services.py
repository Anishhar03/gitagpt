import math

from app.config import Settings
from app.services.embeddings import deterministic_embedding
from app.services.ingestion import split_text
from app.services.providers import LocalProvider, build_grounded_prompt


def test_render_postgres_url_selects_psycopg_driver():
    configured = Settings(database_url="postgresql://user:pass@internal/db")
    assert configured.database_url == "postgresql+psycopg://user:pass@internal/db"


def test_deterministic_embedding_is_stable_and_normalized():
    first = deterministic_embedding("action without attachment")
    second = deterministic_embedding("action without attachment")
    different = deterministic_embedding("steady wisdom")
    assert first == second
    assert first != different
    assert math.isclose(math.sqrt(sum(value * value for value in first)), 1.0)


def test_split_text_preserves_content_with_overlap():
    text = "First teaching. Second teaching explains duty. Third teaching explains steadiness."
    chunks = split_text(text, chunk_size=40, overlap=10)
    assert len(chunks) >= 2
    assert chunks[0].startswith("First teaching")
    assert chunks[-1].endswith("steadiness.")


def test_local_provider_returns_grounded_structure():
    prompt = build_grounded_prompt(
        "How should I act?",
        "Choose wisely",
        [{"title": "Gita", "page_number": 10, "excerpt": "Act with steadiness."}],
    )
    result = LocalProvider().generate(prompt)
    assert "### Reflection" in result
    assert "### Gita perspective" in result
    assert "[Source 1]" in result
