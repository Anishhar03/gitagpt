"""End-to-end local smoke test for Gita GPT.

This validates the no-key path: load the PDF, retrieve passages, build an
answer, and create a transcript PDF.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


os.environ["GITA_GPT_ENGINE"] = "local"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app  # noqa: E402


def main() -> None:
    resources = app.load_runtime_resources()
    answer, sources, notice = app.answer_question(
        resources=resources,
        name="Anish",
        age=23,
        question="How can I stay calm and focused while working?",
        top_k=4,
    )
    transcript = app.build_transcript_pdf(
        "Anish",
        [
            {"role": "user", "content": "How can I stay calm and focused while working?"},
            {"role": "assistant", "content": answer},
        ],
    )

    if resources.mode != "local":
        raise SystemExit(f"Expected local mode, got {resources.mode}.")
    if not answer.strip():
        raise SystemExit("Expected a non-empty answer.")
    if not sources:
        raise SystemExit("Expected at least one retrieved source.")
    if not transcript.startswith(b"%PDF"):
        raise SystemExit("Expected transcript PDF bytes.")
    if notice:
        raise SystemExit(f"Did not expect a runtime notice in local mode: {notice}")

    print("Local smoke test passed.")


if __name__ == "__main__":
    main()
