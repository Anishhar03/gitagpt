from app.database import SessionLocal
from app.models import Chunk, Document
from app.services.embeddings import deterministic_embedding


API = "/api/v1"


def seed_ready_document():
    text = (
        "You have a right to disciplined action, but the outcome is not yours to command. "
        "Steadiness comes from acting with attention while releasing attachment to results."
    )
    with SessionLocal() as db:
        document = Document(
            title="Bhagavad Gita",
            translation="Test translation",
            filename="gita.pdf",
            storage_path="/tmp/gita.pdf",
            checksum="a" * 64,
            status="ready",
            chunk_count=1,
        )
        db.add(document)
        db.flush()
        db.add(
            Chunk(
                document_id=document.id,
                ordinal=0,
                page_number=12,
                content=text,
                token_count=len(text.split()),
                embedding=deterministic_embedding(text),
                source_metadata={"filename": "gita.pdf"},
            )
        )
        db.commit()


def login(client):
    response = client.post(
        f"{API}/auth/dev",
        json={"email": "admin@gitagpt.local", "display_name": "Arjuna"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["role"] == "admin"
    return {"Authorization": f"Bearer {payload['access_token']}"}


def test_health_and_auth_contract(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    assert client.get("/health/ready").status_code == 200
    config = client.get(f"{API}/config").json()
    assert config["auth_mode"] == "development"
    assert config["providers"] == ["local"]
    assert client.get(f"{API}/auth/me").status_code == 401

    headers = login(client)
    profile = client.get(f"{API}/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == "admin@gitagpt.local"


def test_complete_conversation_workflow(client):
    seed_ready_document()
    headers = login(client)

    created = client.post(
        f"{API}/conversations",
        headers=headers,
        json={"title": "New reflection", "intention": "Act with clarity"},
    )
    assert created.status_code == 201
    conversation_id = created.json()["id"]

    answer = client.post(
        f"{API}/conversations/{conversation_id}/messages",
        headers=headers,
        json={"question": "How can I work without fearing the result?"},
    )
    assert answer.status_code == 200
    payload = answer.json()
    assert payload["assistant_message"]["provider"] == "local"
    assert "Gita perspective" in payload["assistant_message"]["content"]
    assert len(payload["sources"]) == 1
    assert payload["sources"][0]["page_number"] == 12

    message_id = payload["assistant_message"]["id"]
    feedback = client.post(
        f"{API}/conversations/messages/{message_id}/feedback",
        headers=headers,
        json={"rating": 1, "comment": "Grounded and useful"},
    )
    assert feedback.status_code == 200
    assert feedback.json()["rating"] == 1

    source_id = payload["sources"][0]["chunk_id"]
    bookmark = client.post(
        f"{API}/knowledge/bookmarks",
        headers=headers,
        json={"chunk_id": source_id, "note": "Review before difficult work"},
    )
    assert bookmark.status_code == 201
    assert len(client.get(f"{API}/knowledge/bookmarks", headers=headers).json()) == 1

    daily = client.get(f"{API}/knowledge/daily", headers=headers)
    assert daily.status_code == 200
    assert daily.json()["source"]["title"] == "Bhagavad Gita"

    transcript = client.get(f"{API}/conversations/{conversation_id}/export", headers=headers)
    assert transcript.status_code == 200
    assert "How can I work" in transcript.text

    detail = client.get(f"{API}/conversations/{conversation_id}", headers=headers).json()
    assert len(detail["messages"]) == 2
