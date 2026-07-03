import hashlib
import re
from pathlib import Path
from uuid import uuid4

from ..config import settings


SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def persist_upload(filename: str, content: bytes) -> tuple[Path, str]:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = SAFE_NAME.sub("-", Path(filename).name).strip("-.") or "document.pdf"
    path = settings.upload_dir / f"{uuid4().hex}-{safe_name}"
    path.write_bytes(content)
    checksum = hashlib.sha256(content).hexdigest()
    return path, checksum


def checksum_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
