"""Global configuration for all Nodus services."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NodusSettings(BaseSettings):
    """Application-wide settings loaded from environment variables / .env."""

    model_config = SettingsConfigDict(
        env_prefix="NODUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Server ──────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 8100
    log_level: str = "info"
    debug: bool = False

    # ── Data paths ──────────────────────────────────────────
    data_dir: Path = Field(default=Path("./data"))
    sqlite_path: Path = Field(default=Path("./data/nodus.db"))
    qdrant_path: Path = Field(default=Path("./data/qdrant"))

    # ── Ollama / LLM ───────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2"
    request_timeout: float = 120.0

    # ── Embedding ──────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    embedding_batch_size: int = 64

    # ── Search ─────────────────────────────────────────────
    default_search_limit: int = 20
    max_search_limit: int = 100
    bm25_weight: float = 0.3
    vector_weight: float = 0.7

    # ── Knowledge graph ────────────────────────────────────
    graph_db_path: Path = Field(default=Path("./data/graph.db"))

    # ── Ingestion ──────────────────────────────────────────
    max_upload_size_mb: int = 100
    chunk_size: int = 512
    chunk_overlap: int = 64

    # ── Security ───────────────────────────────────────────
    allowed_origins: list[str] = Field(default=["http://localhost:1420", "http://127.0.0.1:1420"])
    api_key: str | None = None

    def ensure_dirs(self) -> None:
        """Create required data directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.qdrant_path.mkdir(parents=True, exist_ok=True)
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        self.graph_db_path.parent.mkdir(parents=True, exist_ok=True)


_settings: NodusSettings | None = None


def get_settings() -> NodusSettings:
    """Return the singleton settings instance."""
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = NodusSettings()
    return _settings
