from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    environment: str = "development"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://gitagpt:gitagpt@postgres:5432/gitagpt"
    redis_url: str = "redis://redis:6379/0"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    auth_mode: str = "development"
    jwt_secret: str = "development-only-change-me"
    jwt_ttl_minutes: int = 720
    google_client_id: str = ""
    admin_emails: str = "admin@gitagpt.local"

    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    model_timeout_seconds: float = 20.0

    embedding_dimensions: int = 384
    chunk_size: int = 1200
    chunk_overlap: int = 180
    retrieval_top_k: int = 6
    rate_limit_per_minute: int = 20

    upload_dir: Path = Path("/data/uploads")
    default_pdf_path: Path = Path("/app/gita_book.pdf")
    background_image_path: Path = Path("/app/krishna_ji.jpeg")
    seed_default_document: bool = True
    ingestion_mode: Literal["queue", "inline"] = "queue"
    max_upload_bytes: int = 20 * 1024 * 1024

    service_name: str = "gita-gpt-api"
    log_level: str = "INFO"

    @field_validator("database_url", mode="before")
    @classmethod
    def select_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        return value

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]

    @property
    def admin_email_set(self) -> set[str]:
        return {value.strip().lower() for value in self.admin_emails.split(",") if value.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
