#!/usr/bin/env python3
import json
import os
import time
import urllib.error
import urllib.request


API_ORIGIN = os.getenv("API_ORIGIN", "http://localhost:8000")
WEB_ORIGIN = os.getenv("WEB_ORIGIN", "http://localhost:3000")
API = f"{API_ORIGIN}/api/v1"


def request(url, method="GET", payload=None, token=None, timeout=20, expect_json=True):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read()
        return json.loads(body) if expect_json else body.decode("utf-8")


def wait_for(url, timeout=240):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            request(url)
            return
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def main():
    wait_for(f"{API_ORIGIN}/health/ready")
    wait_for(WEB_ORIGIN)
    config = request(f"{API}/config")
    assert "local" in config["providers"]

    auth = request(
        f"{API}/auth/dev",
        method="POST",
        payload={"email": "admin@gitagpt.local", "display_name": "CI Seeker"},
    )
    token = auth["access_token"]

    deadline = time.time() + 240
    documents = []
    while time.time() < deadline:
        documents = request(f"{API}/knowledge/documents", token=token)
        if any(document["status"] == "ready" for document in documents):
            break
        failed = [document for document in documents if document["status"] == "failed"]
        if failed:
            raise RuntimeError(f"Document indexing failed: {failed}")
        time.sleep(3)
    else:
        raise RuntimeError(f"Document indexing did not finish: {documents}")

    conversation = request(
        f"{API}/conversations",
        method="POST",
        token=token,
        payload={"title": "New reflection", "intention": "CI verification"},
    )
    answer = request(
        f"{API}/conversations/{conversation['id']}/messages",
        method="POST",
        token=token,
        payload={"question": "How can I focus on action instead of fearing the result?"},
    )
    assert answer["assistant_message"]["provider"] == "local"
    assert answer["sources"]

    request(
        f"{API}/conversations/messages/{answer['assistant_message']['id']}/feedback",
        method="POST",
        token=token,
        payload={"rating": 1, "comment": "container smoke test"},
    )
    request(
        f"{API}/knowledge/bookmarks",
        method="POST",
        token=token,
        payload={"chunk_id": answer["sources"][0]["chunk_id"], "note": "CI passage"},
    )
    assert request(f"{API}/knowledge/bookmarks", token=token)
    assert request(f"{API}/knowledge/daily", token=token)["source"]
    transcript = request(
        f"{API}/conversations/{conversation['id']}/export",
        token=token,
        expect_json=False,
    )
    assert "CI verification" in transcript
    print("Gita GPT container smoke test passed.")


if __name__ == "__main__":
    main()
