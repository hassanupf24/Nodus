"""Gateway configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    """Settings specific to the API gateway."""

    model_config = SettingsConfigDict(
        env_prefix="NODUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8100
    debug: bool = False
    log_level: str = "info"
    log_json: bool = False

    allowed_origins: list[str] = [
        "http://localhost:1420",
        "http://127.0.0.1:1420",
        "tauri://localhost",
    ]

    api_key: str | None = None

    # Time-outs for upstream services (seconds)
    llm_timeout: float = 120.0
    default_timeout: float = 30.0


_settings: GatewaySettings | None = None


def get_gateway_settings() -> GatewaySettings:
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = GatewaySettings()
    return _settings
