"""Lightweight repository verification that does not require third-party packages."""

from __future__ import annotations

import ast
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "backend/app/main.py",
    "backend/alembic/versions/20260703_0001_initial.py",
    "backend/tests/test_api.py",
    "frontend/src/App.jsx",
    "frontend/package-lock.json",
    ".github/workflows/ci.yml",
    "docker-compose.yml",
    "render.yaml",
    "requirements.txt",
    ".env.example",
    "gita_book.pdf",
    "krishna_ji.jpeg",
    "docs/ARCHITECTURE.md",
    "docs/API.md",
    "docs/DEPLOYMENT.md",
    "docs/OPERATIONS.md",
    "docs/SECURITY.md",
]

TEXT_FILE_SUFFIXES = {
    ".md",
    ".py",
    ".txt",
    ".toml",
    ".json",
    ".js",
    ".jsx",
    ".css",
    ".sh",
    ".yml",
    ".yaml",
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
    "node_modules",
    "dist",
}

SECRET_PATTERNS = [
    re.compile(r"AIza[0-9A-Za-z_-]+"),
    re.compile(r"ghp_[0-9A-Za-z_]+"),
    re.compile(r"github_pat_[0-9A-Za-z_]+"),
    re.compile(r"gsk_[0-9A-Za-z_]+"),
    re.compile(r"rnd_[0-9A-Za-z_]+"),
]


def assert_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(missing)}")


def assert_python_syntax() -> None:
    paths = list((ROOT / "backend").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py"))
    for path in paths:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def assert_no_example_secret() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    if "AIza" in env_example or "ghp_" in env_example:
        raise SystemExit(".env.example appears to contain a real secret.")


def assert_no_committed_secrets() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(
            part in IGNORED_PARTS or part.startswith(".venv")
            for part in path.relative_to(ROOT).parts
        ):
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
    assert_python_syntax()
    assert_no_example_secret()
    assert_no_committed_secrets()
    print("Project verification passed.")


if __name__ == "__main__":
    main()
