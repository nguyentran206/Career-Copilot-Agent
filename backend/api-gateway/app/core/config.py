from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Career Copilot - API Gateway"
    app_env: str = "development"
    app_version: str = "0.1.0"

    api_prefix: str = "/api/v1"

    host: str = "127.0.0.1"
    port: int = 8000

    frontend_url: str = "http://localhost:3000"

    document_parser_service_url: str = "http://127.0.0.1:8001"
    agent_service_url: str = "http://127.0.0.1:8002"

    document_parser_timeout_seconds: float = Field(default=30.0, gt=0)
    agent_service_timeout_seconds: float = Field(default=150.0, gt=0)

    max_cv_file_size_mb: int = Field(default=5, gt=0)
    max_jd_file_size_mb: int = Field(default=5, gt=0)
    session_ttl_minutes: int = Field(default=30, gt=0)
    max_sessions: int = Field(default=500, gt=0)
    analyze_rate_limit_requests: int = Field(default=10, gt=0)
    analyze_rate_limit_window_seconds: int = Field(default=60, gt=0)
    max_concurrent_analyses: int = Field(default=3, gt=0)

    @property
    def max_cv_file_size_bytes(self) -> int:
        return self.max_cv_file_size_mb * 1024 * 1024

    @property
    def max_jd_file_size_bytes(self) -> int:
        return self.max_jd_file_size_mb * 1024 * 1024

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
