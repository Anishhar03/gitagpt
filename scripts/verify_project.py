"""Lightweight repository verification that does not require third-party packages."""

from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    ".env.example",
    ".streamlit/config.toml",
    "gita_book.pdf",
    "krishna_ji.jpeg",
    "docs/CODE_WALKTHROUGH.md",
    "docs/DEPLOYMENT.md",
    "docs/WORKFLOWS.md",
    "CHANGES.md",
]

TEXT_FILE_SUFFIXES = {
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".json",
    ".example",
}

IGNORED_PARTS = {
    ".git",
    ".venv",
    ".venv2",
    ".codex_deps",
    "__pycache__",
    "codex_deps",
    "gita_chroma",
}

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]+"),
    re.compile(r"ghp_[0-9A-Za-z_]+"),
    re.compile(r"github_pat_[0-9A-Za-z_]+"),
]


def assert_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(missing)}")


def assert_app_syntax() -> None:
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    ast.parse(app_source)


def assert_no_example_secret() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    if "AIza" in env_example or "ghp_" in env_example:
        raise SystemExit(".env.example appears to contain a real secret.")


def assert_no_committed_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts):
            continue
        if path.name == ".env" or path.suffix not in TEXT_FILE_SUFFIXES:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                relative_path = path.relative_to(ROOT)
                raise SystemExit(f"Secret-like value found in {relative_path}.")


def main() -> None:
    assert_required_files()
    assert_app_syntax()
    assert_no_example_secret()
    assert_no_committed_secrets()
    print("Project verification passed.")


if __name__ == "__main__":
    main()
