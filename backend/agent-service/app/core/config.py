from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Career Copilot - Agent Service"
    app_env: str = "development"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    host: str = "127.0.0.1"
    port: int = 8002
    log_level: str = "INFO"

    gemini_enabled: bool = False
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.1-flash-lite"
    gemini_fallback_model: str | None = "gemini-3-flash-preview"
    gemini_embedding_enabled: bool = False
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_timeout_seconds: float = 35.0
    gemini_rate_limit_cooldown_seconds: float = 60.0
    gemini_max_concurrent_requests: int = 2
    gemini_max_server_retries: int = 1
    gemini_retry_backoff_seconds: float = 1.0

    semantic_strong_threshold: float = 0.85
    semantic_partial_threshold: float = 0.70
    scoring_version: str = "phase6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
